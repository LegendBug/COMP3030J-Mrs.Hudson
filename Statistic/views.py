from django.shortcuts import render, get_object_or_404
from Inventory.views import get_all_venues_monthly_consumption, get_monthly_consumption
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
        model_path = '../static/model/fasterrcnn_resnet50_fpn_v2_coco.pth'
        model = fasterrcnn_resnet50_fpn_v2(weights=None, box_score_thresh=0.01)
        model.load_state_dict(torch.load(model_path))
        model.eval()
        weights = FasterRCNN_ResNet50_FPN_V2_Weights.COCO_V1
        preprocess = weights.transforms()


@csrf_exempt
def recognize_flow(request):
    if request.method == 'POST' and request.FILES.get('image'):
        load_model()  # 确保模型已经加载

        uploaded_image = request.FILES['image']

        # 将上传的图像转换为 PIL 图像
        img = Image.open(uploaded_image)
        img = img.convert("RGB")

        # 将 PIL 图像转换为张量
        img_tensor = preprocess(img)

        # 进行推理
        with torch.no_grad():
            prediction = model([img_tensor])[0]
        labels = [weights.meta["categories"][i] for i in prediction["labels"]]

        # 统计person实例的数量
        person_count = sum([1 for label in prediction["labels"] if label == 1])  # 假设标签1对应“person”

        # 在图像上绘制边界框
        boxes = draw_bounding_boxes(img_tensor, boxes=prediction["boxes"], labels=labels, colors="red", width=4)
        result_img = to_pil_image(boxes.detach())

        # 将图像转换为 base64 编码
        buffer = io.BytesIO()
        result_img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # 返回包含 base64 图像和行人数目的 JSON 响应
        return JsonResponse({'image': img_str, 'person_count': person_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)
