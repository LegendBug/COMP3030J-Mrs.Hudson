import json
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from torchvision.io.image import read_image
from Inventory.views import get_all_venues_monthly_consumption, get_monthly_consumption
from Layout.models import SpaceUnit
from Layout.serializers import SpaceUnitSerializer
from Statistic.models import Monitor, Capture
from Venue.models import Venue
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io
import base64
import json


def get_venues(request):
    venues = Venue.objects.all().values_list('name', flat=True)
    return JsonResponse(list(venues), safe=False)


def get_consumption_data(request, year):
    # 获取整合了用水量和用电量的统计数据
    combined_statistics = get_all_venues_monthly_consumption(year)

    # 分别存储用水量和用电量的数据字典
    water_statistics = {}
    electric_statistics = {}

    for month_data in combined_statistics:
        month_num = month_data[0]
        formatted_month = f"Month {month_num}"
        total_water = month_data[1]['total_water']
        total_power = month_data[1]['total_power']

        # 将用水量和用电量数据分别存储在对应的字典中
        water_statistics[formatted_month] = total_water
        electric_statistics[formatted_month] = total_power

    # 返回用水量和用电量的数据字典
    return JsonResponse({'water_statistics': water_statistics, 'electric_statistics': electric_statistics})


def get_consumption_data_by_venue(request, venue_name, year):
    # 获取整合了用水量和用电量的统计数据
    venue = get_object_or_404(Venue, name=venue_name)
    combined_statistics = get_monthly_consumption(year, venue)

    # 分别存储用水量和用电量的数据字典
    water_statistics = {}
    electric_statistics = {}

    for month_data in combined_statistics:
        month_num = month_data[0]
        formatted_month = f"Month {month_num}"
        total_water = month_data[1]['total_water']
        total_power = month_data[1]['total_power']

        # 将用水量和用电量数据分别存储在对应的字典中
        water_statistics[formatted_month] = total_water
        electric_statistics[formatted_month] = total_power

    # 返回用水量和用电量的数据字典
    return JsonResponse({'water_statistics': water_statistics, 'electric_statistics': electric_statistics})


def statistic(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
    return render(request, 'Statistic/statistic.html', {'user_type': user_type})


# water_statistics = {
#     "Month 1": 1200,
#     "Month 2": 1600,
#     "Month 3": 1000,
#     "Month 4": 800,
#     "Month 5": 900,
#     "Month 6": 1600,
#     "Month 7": 2100,
#     "Month 8": 2200,
#     "Month 9": 1800,
#     "Month 10": 1500,
#     "Month 11": 1300,
#     "Month 12": 900,
# }
#
# # 生成用电量的假数据
# electric_statistics = {
#     "Month 1": 100,
#     "Month 2": 1600,
#     "Month 3": 1000,
#     "Month 4": 800,
#     "Month 5": 900,
#     "Month 6": 1600,
#     "Month 7": 210,
#     "Month 8": 2200,
#     "Month 9": 1800,
#     "Month 10": 150,
#     "Month 11": 1300,
#     "Month 12": 900,
# }


model = None
weights = None
preprocess = None


def load_model():
    global model, preprocess, weights
    if model is None:
        model_path = os.path.join(settings.BASE_DIR, 'static', 'model', 'fasterrcnn_resnet50_fpn_v2_coco.pth')
        model = fasterrcnn_resnet50_fpn_v2(weights=None, box_score_thresh=0.01)
        model.load_state_dict(torch.load(model_path))
        model.eval()
        weights = FasterRCNN_ResNet50_FPN_V2_Weights.COCO_V1
        preprocess = weights.transforms()


@csrf_exempt
def recognize_flow(request):  # {url (Statistic:recognize_flow)}
    if request.method == 'POST' and request.FILES.get('image'):
        load_model()  # 确保模型已经加载

        uploaded_image = request.FILES['image']
        img = Image.open(uploaded_image).convert("RGB")

        # 将 PIL 图像转换为张量并进行预处理
        img_tensor = preprocess(img).float()

        # 进行推理
        with torch.no_grad():
            prediction = model([img_tensor])[0]

        labels = [weights.meta["categories"][i] for i in prediction["labels"]]

        # 统计person实例的数量
        person_count = sum(1 for label in prediction["labels"] if label == 1)

        # 在图像上绘制边界框之前，将图像张量转换回uint8
        img_uint8 = (img_tensor * 255).byte()  # 假设img_tensor已经归一化到[0, 1]

        # 绘制边界框
        boxes = draw_bounding_boxes(img_uint8, boxes=prediction["boxes"], labels=labels, colors="red", width=4)
        result_img = to_pil_image(boxes)

        # 将图像转换为 base64 编码
        buffer = io.BytesIO()
        result_img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # 返回包含 base64 图像和行人数目的 JSON 响应
        return JsonResponse({'image': img_str, 'person_count': person_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def capture(request, monitor_id):
    if request.method == 'POST' and request.FILES.get('image'):
        load_model()  # 确保模型已经加载

        monitor = get_object_or_404(Monitor, id=monitor_id)
        uploaded_image = request.FILES['image']
        img = Image.open(uploaded_image).convert("RGB")

        # 将 PIL 图像转换为张量并进行预处理
        img_tensor = preprocess(img).float()

        # 进行推理
        with torch.no_grad():
            prediction = model([img_tensor])[0]

        labels = [weights.meta["categories"][i] for i in prediction["labels"]]

        # 统计person实例的数量
        person_count = sum(1 for label in prediction["labels"] if label == 1)

        # 在图像上绘制边界框之前，将图像张量转换回uint8
        img_uint8 = (img_tensor * 255).byte()  # 假设img_tensor已经归一化到[0, 1]

        # 绘制边界框
        boxes = draw_bounding_boxes(img_uint8, boxes=prediction["boxes"], labels=labels, colors="red", width=4)
        result_img = to_pil_image(boxes)

        # 将图像转换为 base64 编码
        buffer = io.BytesIO()
        result_img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # 创建Capture记录
        Capture.objects.create(monitor=monitor, flow_number=person_count)

        # 返回包含 base64 图像和行人数目的 JSON 响应
        return JsonResponse({'image': img_str, 'person_count': person_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def monitor_venue(request):
    user_type = request.session.get('user_type', 'Guest')
    if user_type == 'Manager':
        current_access_id = request.session.get('venue_id')
        current_access = Venue.objects.get(pk=current_access_id)
    else:
        return redirect('Venue:home')
    return render(request, 'Statistic/monitor.html',
                  {'current_access': current_access, 'user_type': user_type,
                   'sectors': current_access.sectors.filter(parent_unit=None).order_by('created_at'),
                   })


def refresh_data(request):
    if request.method == 'GET':
        # 从GET请求中获取参数
        current_sector_id = int(request.GET.get('current_sector_id', 0))
        current_access_id = int(request.GET.get('current_access_id', 0))
        user_type = request.GET.get('user_type')
        # 验证数据有效性
        if (current_sector_id is None) or (current_access_id is None) or (
                user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=400)
        # 获取当前正在访问的位置
        if current_sector_id == 0:  # 说明用户是首次访问Layout页面, 根据用户类型获取当前访问Venue/Exhibition/Booth的第一个sector
            current_sector_id = get_object_or_404(Venue, id=current_access_id).sectors.first().id

        root = get_object_or_404(SpaceUnit, id=current_sector_id)
        # 返回JSON化的root数据
        if root is not None:
            # 使用Serializer序列化root
            serializer = SpaceUnitSerializer(root)
            return JsonResponse(serializer.data)  # 使用Django的JsonResponse返回数据
        else:
            return JsonResponse({'error': 'No root SpaceUnit found for the specified sector!'},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def synchronize_monitors_data(request):  # 该方法与edit_element方法的区别是, 该方法只被用于Konva对象在画板上进行位移或变换后刷新Konva对象在后端的data属性中的数据
    if request.method == 'POST':
        data = json.loads(request.body)  # 使用 json.loads 解析请求体中的 JSON 数据
        root_data = data.get('root')
        if not root_data:
            return JsonResponse({'error': 'No root space unit provided.'}, status=400)

        def recursively_update(new_dic_data):  # 递归更新树结构的SpaceUnit其下的所有Monitor
            new_monitors_dic_data = new_dic_data.get('monitors')
            for i in range(len(new_monitors_dic_data)):
                old_monitor = get_object_or_404(Monitor, id=int(new_monitors_dic_data[i].get('id')))
                new_element_data = new_monitors_dic_data[i]
                # 更新KonvaElement实例
                old_monitor.data = new_element_data.get('data')
                old_monitor.save()

            # 递归更新子SpaceUnit下的所有KonvaElement
            if (len(new_dic_data.get('child_units')) > 0):
                for i in range(len(new_dic_data.get('child_units'))):
                    if (len(new_dic_data.get('child_units')[i].get('monitors')) > 0):
                        recursively_update(new_dic_data.get('child_units')[i])

        recursively_update(root_data)
        return JsonResponse({'success': 'The data has been successfully synchronized!'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def add_monitor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_online = request.POST.get('is_online', 'true') == 'true'
        transformable = request.POST.get('transformable', 'true') == 'true'
        monitor_data = request.POST.get('data')
        layer_id = request.POST.get('layer_id')

        layer = get_object_or_404(SpaceUnit, id=layer_id)
        venue = layer.affiliation
        # 创建KonvaElement实例
        monitor = Monitor.objects.create(
            name=name,
            venue=venue,
            is_online=is_online,
            layer=layer,
            data=monitor_data,
            transformable=transformable,
        )

        updated_monitor_data = json.loads(monitor_data)
        updated_monitor_data["attrs"]["id"] = f"{monitor.pk}"  # 添加id属性
        monitor.data = json.dumps(updated_monitor_data)  # 更新已创建的KonvaElement实例的data字段
        monitor.save()

        # 返回新创建的KonvaElement的信息
        return JsonResponse({
            'id': monitor.id,
            'name': monitor.name,
            'layer': monitor.layer.id if monitor.layer else None,
            'data': monitor.data,
            'image_url': monitor.image.url if monitor.image else None
        }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def edit_monitor(request):  # {url (Layout:edit_element)}
    if request.method == 'POST':
        element_id = request.POST.get('id')
        name = request.POST.get('name')
        is_online = request.POST.get('is_online', 'true') == 'true'
        transformable = request.POST.get('transformable', 'true') == 'true'
        monitor_data = request.POST.get('data')

        monitor = get_object_or_404(Monitor, id=element_id)
        # 更新Monitor实例
        monitor.name = name
        monitor.is_online = is_online
        monitor.transformable = transformable
        monitor.data = monitor_data
        monitor.save()

        # 返回新创建的KonvaElement的信息
        return JsonResponse({
            'id': monitor.id,
            'name': monitor.name,
            'layer': monitor.layer.id if monitor.layer else None,
            'data': monitor.data,
            'image_url': monitor.image.url if monitor.image else None
        }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_monitor(request):
    if request.method == 'GET':
        monitor_id = int(request.GET.get('element_id', 0))
        monitor = get_object_or_404(Monitor, id=monitor_id)
        monitor.delete()  # 删除元素
        return JsonResponse({'success': 'The element has been successfully deleted!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
