from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils import timezone

from Exhibition.forms import ExhibApplicationForm, FilterExhibitionsForm
from Venue.forms import CreateVenueForm
from Venue.models import Venue
from django.contrib import messages


def home(request):
    if request.method == 'GET':
        # GET请求，展示场馆列表和空的创建表单
        venues = Venue.objects.all()
        form = CreateVenueForm()  # 创建一个空的表单实例
        return render(request, 'Venue/home.html',
                      {'venues': venues, 'user_type': request.session.get('user_type', 'Guest'),
                       'messages': messages.get_messages(request),
                       'form': form})
    else:  # POST请求
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'error': 'Permission denied!'}, status=403)
        form = CreateVenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue created successfully!'}, status=201)
        else:
            first_error_key, first_error_messages = list(form.errors.items())[0]
            first_error_message = first_error_key + ': ' + first_error_messages[0]
            return JsonResponse({'error': first_error_message}, status=400)


def modify_venue(request, venue_id):
    if request.method == 'POST':
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'error': 'Permission denied!'}, status=403)
        venue = Venue.objects.filter(id=venue_id).first()
        if venue is None:
            return JsonResponse({'error': 'Venue not found!'}, status=404)
        form = CreateVenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue modified successfully!'}, status=201)
        else:
            first_error_key, first_error_messages = list(form.errors.items())[0]
            first_error_message = first_error_key + ': ' + first_error_messages[0]
            return JsonResponse({'error': first_error_message}, status=400)
    else:
        return HttpResponseNotAllowed(['POST'])


def delete_venue(request, venue_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
        return JsonResponse({'error': 'Permission denied!'}, status=403)
    venue = Venue.objects.filter(id=venue_id).first()
    if venue is None:
        return JsonResponse({'error': 'Venue not found!'}, status=404)
    venue.delete()
    return JsonResponse({'success': 'Venue deleted successfully!'})


def venue(request, venue_id): # TODO 在展览过期后, 将绑定的SpaceUnit的affiliation字段置空（启动定时任务）
    current_venue = Venue.objects.filter(id=venue_id).first()
    if current_venue is None:
        return redirect('Venue:home')

    request.session['venue_id'] = venue_id  # 将venue_id存入session
    user_type = request.session.get('user_type', 'Guest')
    exhibitions = None
    if request.method == 'GET':
        # 筛选start_at在当前时间或者之后的展览,并按照从最近开始到最远开始的顺序排序
        exhibitions = current_venue.exhibitions.filter(start_at__gte=timezone.now()).order_by('start_at')
    elif request.method == 'POST':
        submitted_filter_form = FilterExhibitionsForm(request.POST)
        if submitted_filter_form.is_valid():
            exhibitions = submitted_filter_form.filter()
            messages.success(request, 'Filter exhibitions success!')
        else:
            first_error_key, first_error_messages = list(submitted_filter_form.errors.items())[0]
            first_error_message = first_error_key + ': ' + first_error_messages[0]
            return JsonResponse({'error': first_error_message}, status=400)
    # 将展览信息转换为字典
    exhibitions_list = []
    for exhibition in exhibitions:
        sectors = ''
        for sector in exhibition.sectors.all():
            sectors += sector.name + ' '
        stage = exhibition.exhibition_application.get_stage_display()
        # TODO 修复展览状态不对的问题
        if stage == 'REJECTED':  # 展览申请被拒绝
            continue
        elif stage == 'ACCEPTED':
            stage = '✅ ACCEPTED'
        elif exhibition.end_at < timezone.now():  # 展览已结束
            stage = '🔴 OUTDATED'
        elif exhibition.start_at < timezone.now() < exhibition.end_at:  # 展览进行中
            stage = '🟢 UNDERWAY'
        else:
            stage = '🟠 PENDING'
        exhibitions_list.append({
            'id': exhibition.id,
            'name': exhibition.name,
            'description': exhibition.description,
            'sectors': sectors,
            'start_at': exhibition.start_at,
            'end_at': exhibition.end_at,
            'image': exhibition.image.url,
            'organizer': exhibition.organizer.detail.username,
            'stage': stage
        })

    return render(request, 'Venue/venue.html', {
        'venue': current_venue,
        'exhibitions': exhibitions_list,
        'floor_range': range(1, current_venue.floor + 1),
        'user_type': user_type,
        'filter_form': FilterExhibitionsForm(),
        'application_form': ExhibApplicationForm(
            initial={'affiliation_content_type': ContentType.objects.get_for_model(current_venue),
                     'affiliation_object_id': venue_id})
    })
