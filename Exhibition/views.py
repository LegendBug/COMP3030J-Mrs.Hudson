from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from rest_framework import status
from django.utils import timezone

from Booth.forms import BoothApplicationForm, FilterBoothsForm
from Booth.views import cancel_booth
from Exhibition.forms import ExhibApplicationForm
from Exhibition.models import Exhibition, ExhibitionApplication
from Layout.serializers import SpaceUnitSerializer
from django.contrib import messages

from User.models import Application


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
    application = current_exhibition.exhibition_application
    if application.stage == Application.Stage.CANCELLED or application.stage == Application.Stage.REJECTED:
        return redirect('Venue:venue', venue_id=current_exhibition.venue.pk)

    # 判断当前是否为展览的拥有者
    user_type = request.session.get('user_type', '')
    if user_type == 'Manager' or request.user == application.applicant:
        is_owner = True
    else:
        is_owner = False

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
            if sector.inherit_from is not None:
                sectors += sector.name + ' '
        stage = booth.booth_application.get_stage_display()

        if stage == 'REJECTED' or stage == 'CANCELLED':  # 展览申请被拒绝(不显示)
            continue
        elif stage == 'ACCEPTED':
            stage = '✅ ACCEPTED'
            if booth.end_at < timezone.now():  # 展览已结束
                stage = '🔴 OUTDATED'
            elif booth.start_at < timezone.now() < booth.end_at:  # 展览进行中
                stage = '🟢 UNDERWAY'
        elif stage == 'INITIAL_SUBMISSION':
            stage = '🟠 PENDING'
        else:
            continue
        booth_list.append({
            'id': booth.id,
            'name': booth.name,
            'description': booth.description,
            'image': booth.image.url,
            'start_at': booth.start_at,
            'end_at': booth.end_at,
            'exhibitor': booth.exhibitor.detail.username,
            'sectors': sectors,
            'stage': stage
        })

    return render(request, 'System/exhibition.html', {
        'exhibition': current_exhibition,
        'booths': booth_list,
        'sectors': current_exhibition.sectors.filter(inherit_from__isnull=False).order_by('created_at'),
        'is_owner': is_owner,
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
        if sector_id == 0:  # 说明当前请求时用户初次进入展览页面, 返回当前展会的第一个Sector
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
        form = ExhibApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.create_application(request)
                return JsonResponse({'success': 'Exhibition application created successfully!'}, status=200)
            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
        else:
            first_error_key, first_error_messages = list(form.errors.items())[0]
            first_error_message = first_error_key + ': ' + first_error_messages[0]
            return JsonResponse({'error': first_error_message}, status=400)
    else:
        return HttpResponseNotAllowed(['POST'])


# 取消操作包括手动取消申请和自动结束
@login_required
def cancel_exhibition(request, exhibition_id):
    if request.method == 'POST':
        exhibition = Exhibition.objects.filter(id=exhibition_id).first()
        application = ExhibitionApplication.objects.filter(exhibition_id=exhibition_id).first()
        if exhibition_id is None or application is None:
            return JsonResponse({'error': 'Exhibition not found'}, status=404)

        # 自动结束，展览结束时间已经过了
        if exhibition.end_at < timezone.now():
            pass
        # 手动取消，管理员强制取消，或申请处于初始提交阶段
        elif hasattr(request.user, 'manager') or application.stage == Application.Stage.INITIAL_SUBMISSION:
            application.stage = Application.Stage.CANCELLED
            application.save()
        else:
            return JsonResponse({'error': 'Exhibition application cannot be canceled at this stage'}, status=400)

        # 删除包含的展台申请关联的展位
        for booth in exhibition.booths.all():
            cancel_booth(request, booth.id)

        # 删除全部的展位申请关联的sectors
        for sector in exhibition.sectors.all():
            sector.delete()
        # TODO 锁定全部的资源
        return JsonResponse({'success': 'Exhibition application canceled successfully!'}, status=200)
    else:
        return HttpResponseNotAllowed(['POST'])
