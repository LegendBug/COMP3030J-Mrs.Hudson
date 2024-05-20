from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from rest_framework import status
from django.utils import timezone
from Booth.forms import BoothApplicationForm, FilterBoothsForm
from Exhibition.forms import ExhibApplicationForm
from Exhibition.models import Exhibition, ExhibitionApplication
from Layout.serializers import SpaceUnitSerializer
from User.models import Message, MessageDetail, Organizer, Manager, Exhibitor
from Venue.models import Venue
from django.contrib import messages


@login_required
def exhibition(request, exhibition_id):
    current_exhibition = Exhibition.objects.filter(id=exhibition_id).first()
    if current_exhibition is None:
        venue_id = request.session.get('venue_id', None)
        if venue_id:
            return redirect('Venue:venue', venue_id=venue_id)
        else:
            return redirect('Venue:home')
    request.session['exhibition_id'] = exhibition_id  # 将exhibition_id存入session

    user_type = request.session.get('user_type', 'Guest')
    booths = None
    if request.method == 'GET':
        # 筛选end_at在今日或者今日之后的展台,并按照从最近开始到最远开始的顺序排序
        booths = current_exhibition.booths.filter(start_at__lte=timezone.now()).order_by('-start_at')
    elif request.method == 'POST':
        submitted_filter_form = FilterBoothsForm(request.POST)
        if submitted_filter_form.is_valid():
            booths = submitted_filter_form.filter()
            messages.success(request, 'Filter exhibitions success!')
        else:
            first_error_key, first_error_messages = list(submitted_filter_form.errors.items())[0]
            first_error_message = first_error_key + ': ' + first_error_messages[0]
            return JsonResponse({'error': first_error_message}, status=400)

    # 将展区信息转换为字典
    booth_list = []
    for booth in booths:
        sectors = ''
        for sector in booth.sectors.all():
            sectors += sector.name + ' '
        booth_list.append({
            'id': booth.id,
            'name': booth.name,
            'description': booth.description,
            'image': booth.image.url,
            'start_at': booth.start_at,
            'end_at': booth.end_at,
            'exhibitor': booth.exhibitor.detail.username,
            'sectors': sectors,
        })

    return render(request, 'Exhibition/exhibition.html', {
        'exhibition': current_exhibition,
        'booths': booth_list,
        'sectors': current_exhibition.sectors.all(),
        'user_type': user_type,
        'filter_form': FilterBoothsForm(),
        'application_form': BoothApplicationForm(
            initial={'affiliation_content_type': ContentType.objects.get_for_model(current_exhibition),
                     'affiliation_object_id': exhibition_id}),
    })


def refresh_data(request):
    if request.method == 'GET':
        # 从GET请求中获取参数
        sector_id = int(request.GET.get('sector_id', 0))
        exhibition_id = int(request.GET.get('exhibition_id', 0))
        user_type = request.GET.get('user_type')
        # 验证数据有效性
        if (sector_id is None) or (exhibition_id is None) or (user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=400)
        current_exhibition = get_object_or_404(Exhibition, pk=exhibition_id)
        if sector_id == 0: # 说明当前请求时用户初次进入展览页面, 返回当前展会的第一个Sector
            sector_id = current_exhibition.sectors.first().id
        # 获取当前场馆的当前楼层的Root SpaceUnit节点(parent_unit=None 且创建时间最早)
        root = current_exhibition.sectors.filter(pk=sector_id).order_by('created_at').first()
        # 返回JSON化的root数据
        if root is not None:
            # 使用Serializer序列化root
            serializer = SpaceUnitSerializer(root)
            return JsonResponse(serializer.data)  # 使用Django的JsonResponse返回数据
        else:
            return JsonResponse({'error': 'No root SpaceUnit found for the specified floor'},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


# 创建展览申请
@login_required
def create_exhibit_application(request):
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'organizer'):
                return JsonResponse({'error': 'Permission denied!'}, status=403)
            # 获取POST请求中的数据
            form = ExhibApplicationForm(request.POST, request.FILES)
            if not form.is_valid():
                # 获取第一个错误信息
                first_error_key, first_error_messages = list(form.errors.items())[0]
                first_error_message = first_error_key + ': ' + first_error_messages[0]
                return JsonResponse({'error': first_error_message}, status=400)
            venue_id = form.cleaned_data.get('venue_id')
            name = form.cleaned_data.get('exhib_name')
            description = form.cleaned_data.get('exhib_description')
            start_at = form.cleaned_data.get('exhib_start_at')
            end_at = form.cleaned_data.get('exhib_end_at')
            image = form.cleaned_data.get('exhib_image')
            sectors = form.cleaned_data.get('exhib_sectors')
            content = form.cleaned_data.get('message_content')

            # 创建新的展览和展览申请
            venue = Venue.objects.get(pk=venue_id)
            organizer = Organizer.objects.get(detail=request.user)
            new_exhibition = Exhibition.objects.create(
                name=name, description=description, start_at=start_at, end_at=end_at,
                image=image, organizer=organizer, venue=venue
            )
            for sector in sectors:
                sector.available = False
            new_exhibition.sectors.set(sectors)  # 反向关系需要使用set方法
            new_exhib_application = ExhibitionApplication.objects.create(applicant=request.user,
                                                                         description=description,
                                                                         exhibition=new_exhibition)
            new_exhibition.exhibition_application = new_exhib_application
            new_exhibition.save()
            new_exhib_application.save()
            # 创建提示消息和消息详情
            new_message = Message.objects.create(title="New Exhibition Application for '" + name + "'",
                                                 sender=request.user, recipient=Manager.objects.first().detail)
            application_type = ContentType.objects.get_for_model(new_exhib_application)
            new_message_detail = MessageDetail.objects.create(message=new_message, content=content,
                                                              application_object_id=new_exhib_application.id,
                                                              application_content_type=application_type)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Exhibition application created successfully!'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
