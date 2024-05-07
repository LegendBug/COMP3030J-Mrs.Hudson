from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from Exhibition.forms import ExhibApplicationForm, FilterExhibitionsForm
from User.models import Exhibitor
from Venue.forms import CreateVenueForm
from Venue.models import Venue
from Exhibition.models import Exhibition
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
            return JsonResponse({'errors': 'Permission denied!'}, status=403)
        form = CreateVenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue created successfully!'})
        else:
            # {"name": [{"message": "This field is required.", "code": "required"}], "address": [{"message": "This field is required.", "code": "required"}], "floor": [{"message": "This field is required.", "code": "required"}], "image": [{"message": "This field is required.", "code": "required"}]}
            return JsonResponse({'errors': form.errors.as_json()}, status=400)  # TODO 此处前端没有遍历errors,导致报错消息无法显示


# TODO 在展览过期后，将绑定的SpaceUnit的affiliation字段置空
def venue(request, venue_id):
    current_venue = Venue.objects.filter(id=venue_id).first()
    if current_venue is None:
        return redirect('Venue:home')
    request.session['venue_id'] = venue_id  # 将venue_id存入session

    user = request.user
    user_type = request.session.get('user_type', 'Manager')
    exhibitions = None

    if request.method == 'GET':
        # 根据用户类型筛选展览信息
        if user not in [None, ''] and hasattr(user, 'manager'):
            exhibitions = current_venue.exhibitions.all()
        elif user not in [None, ''] and hasattr(user, 'organizer'):
            exhibitions = current_venue.exhibitions.filter(organizer=user.organizer)
        else:  # 参展方
            exhibitions = current_venue.exhibitions.all()
            # current_exhibitions = current_venue.exhibitions.all()
            # booths = Exhibitor.objects.filter(detail=user).first().booths.all()
            # exhibitions = []
            # for booth in booths:
            #     if booth.exhibition in current_exhibitions:
            #         exhibitions.append(booth.exhibition)

    elif request.method == 'POST':
        submitted_filter_form = FilterExhibitionsForm(request.POST)
        if submitted_filter_form.is_valid():
            exhibitions = submitted_filter_form.filter()
            messages.success(request, 'Filter exhibitions success!')
        else:
            exhibitions = Exhibition.objects.none()
            # messages.error(request, 'Filter exhibitions failed! Please check the form.')
    # 将展览信息转换为字典
    exhibitions_data = []
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
        exhibitions_data.append({
            'id': exhibition.id,
            'name': exhibition.name,
            'description': exhibition.description,
            'sectors': sectors,
            'start_at': exhibition.start_at,
            'end_at': exhibition.end_at,
            'image': exhibition.image.url if exhibition.image else None,
            'organizer': exhibition.organizer.detail.username,
            'stage': stage
        })
    affiliation_type = ContentType.objects.get_for_model(current_venue)  # 获取场馆的ContentType
    application_form = ExhibApplicationForm(
        initial={'affiliation_content_type': affiliation_type, 'affiliation_object_id': venue_id})  # 传入当前Type和场馆的id
    filter_form = FilterExhibitionsForm()
    return render(request, 'Venue/venue.html', {
        'exhibitions': exhibitions_data,
        'venue': current_venue,
        'user_type': user_type,
        'application_form': application_form,
        'filter_form': filter_form
    })


def modify_venue(request, venue_id):
    if request.method == 'GET':
        venue = Venue.objects.filter(id=venue_id).first()
        if venue is None:
            return redirect('Venue:home')
        form = CreateVenueForm(instance=venue)
        return render(request, 'Venue/modify_venue.html', {'form': form})
    else:
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'errors': 'Permission denied!'}, status=403)
        venue = Venue.objects.filter(id=venue_id).first()
        if venue is None:
            return JsonResponse({'errors': 'Venue not found!'}, status=404)
        form = CreateVenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue modified successfully!'})
        else:
            return JsonResponse({'errors': form.errors.as_json()}, status=400)


def delete_venue(request, venue_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
        return JsonResponse({'errors': 'Permission denied!'}, status=403)
    venue = Venue.objects.filter(id=venue_id).first()
    if venue is None:
        return JsonResponse({'errors': 'Venue not found!'}, status=404)
    venue.delete()
    return JsonResponse({'success': 'Venue deleted successfully!'})
