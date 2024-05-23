from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from rest_framework import status
from Booth.forms import BoothApplicationForm
from Booth.models import Booth
from Layout.serializers import SpaceUnitSerializer


@login_required
def booth(request, booth_id):
    if request.method == 'GET':
        current_booth = Booth.objects.filter(id=booth_id).first()
        if current_booth is None:
            exhibition_id = request.session.get('exhibition_id', None)
            if exhibition_id:
                return redirect('Exhibition:exhibition', exhibition_id=exhibition_id)
            else:
                return redirect('Venue:home')
        request.session['booth_id'] = booth_id  # 将booth_id存入session
        return render(request, 'Booth/../templates/System/booth.html', {
            'booth': current_booth,
            'sectors': current_booth.sectors.all(),
            'user_type': request.session.get('user_type', 'Guest'),
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
