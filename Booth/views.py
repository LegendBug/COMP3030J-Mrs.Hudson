from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from rest_framework import status
from Booth.forms import BoothApplicationForm
from Booth.models import Booth, BoothApplication
from Layout.serializers import SpaceUnitSerializer
from User.models import Application


@login_required
def booth(request, booth_id):
    if request.method == 'GET':
        print(booth_id)
        current_booth = Booth.objects.filter(id=booth_id).first()
        if current_booth is None:
            exhibition_id = request.session.get('exhibition_id', None)
            if exhibition_id:
                return redirect('Exhibition:exhibition', exhibition_id=exhibition_id)
            else:
                return redirect('Venue:home')
        request.session['booth_id'] = booth_id  # 将booth_id存入session
        application = current_booth.booth_application
        if application.stage == Application.Stage.CANCELLED or application.stage == Application.Stage.REJECTED:
            return redirect('Exhibition:exhibition', exhibition_id=current_booth.exhibition.pk)

        # 判断当前是否为展览的拥有者(管理员，申请者或该展览的举办方)
        user_type = request.session.get('user_type', '')
        if (user_type != 'Manager'
                and request.user != current_booth.exhibition.organizer.detail
                and request.user != application.applicant):
            is_owner = False
        else:
            is_owner = True

        print(is_owner)
        return render(request, 'System/booth.html', {
            'booth': current_booth,
            'sectors': current_booth.sectors.all(),
            'is_owner': is_owner,
            'user_type': user_type,
        })
    else:
        return HttpResponseNotAllowed(['GET'])


def refresh_data(request):
    if request.method == 'GET':
        # 从GET请求中获取参数
        sector_id = int(request.GET.get('sector_id', 0))
        booth_id = int(request.GET.get('booth_id', 0))
        user_type = request.GET.get('user_type')
        # 验证数据有效性
        if (sector_id is None) or (booth_id is None) or (user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=400)
        current_exhibition = get_object_or_404(Booth, pk=booth_id)
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


@login_required
def create_booth_application(request):
    if request.method == 'POST':
        form = BoothApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.create_application(request)
                return JsonResponse({'success': 'Booth application created successfully!'}, status=200)
            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Internal server error.', 'details': str(e)}, status=500)
        else:
            first_error_key, first_error_messages = list(form.errors.items())[0]
            first_error_message = f"{first_error_key}: {first_error_messages[0]}"
            return JsonResponse({'error': first_error_message}, status=400)
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def cancel_booth(request, booth_id):
    if request.method == 'POST':
        booth = Booth.objects.filter(id=booth_id).first()
        application = BoothApplication.objects.filter(booth_id=booth_id).first()
        if booth_id is None or application is None:
            return JsonResponse({'error': 'Booth not found'}, status=404)

        # 自动结束，展览结束时间已经过了
        if booth.end_at < timezone.now():
            pass
        # 手动取消，管理员强制取消，或申请处于初始提交阶段
        elif hasattr(request.user, 'manager') or application.stage == Application.Stage.INITIAL_SUBMISSION:
            application.stage = Application.Stage.CANCELLED
            application.save()
        else:
            return JsonResponse({'error': 'Exhibition application cannot be canceled at this stage'}, status=400)

        # 删除展台申请关联的sector
        for sector in booth.sectors.all():
            sector.delete()

        # 归还全部物品
        for item in booth.items.all():
            if item.affiliation != item.category.origin:
                item.affiliation_content_type = ContentType.objects.get_for_model(item.category.origin)
                item.affiliation_object_id = item.category.origin.pk
                item.is_using = 0
                item.save()
        for category in booth.inventory_categories.all():
            category.delete()
        return JsonResponse({'success': 'Booth application canceled successfully!'}, status=200)
    else:
        return HttpResponseNotAllowed(['POST'])
