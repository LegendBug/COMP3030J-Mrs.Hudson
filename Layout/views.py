from django.shortcuts import render
from rest_framework import status

from Booth.models import Booth
from Exhibition.models import Exhibition
from Venue.models import Venue
from django.http import JsonResponse
from .forms import AddLayerForm, EditLayerForm
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

def venue_layout(request):
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    # 获取当前场馆的items
    items = venue.items.all()
    # add_layer_form
    add_sublayer_form = AddLayerForm(initial={'parent_id': 1, 'floor': venue.floor})
    return render(request, 'Layout/venue_layout.html',
                  {'venue': venue, 'items': items, 'user_type': user_type, 'floor_range': range(1, venue.floor),
                   'add_sublayer_form': add_sublayer_form})


def layout(request):
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
    # 获取当前场馆的items
    items = venue.items.all()
    # add_layer_form
    add_sublayer_form = AddLayerForm(initial={'parent_id': 1, 'floor': venue.floor})
    edit_layer_form = EditLayerForm()
    return render(request, 'Layout/layout.html',
                  {'current_access': venue, 'user_type': user_type, 'items': items, 'floor_range': range(1, venue.floor + 1),
                   'add_sublayer_form': add_sublayer_form, 'edit_layer_form': edit_layer_form})


def synchronize_data(request):  # {url (Layout:get_floor_data)}
    if request.method == 'GET':
        # 从GET请求中获取参数
        floor = int(request.GET.get('floor', "1"))
        current_access_id = int(request.GET.get('current_access_id', 0))
        user_type = request.GET.get('user_type')
        # 验证数据有效性
        if (floor < 1) or (current_access_id < 1) or (user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取当前正在访问的位置
        if user_type == 'Manager':
            current_access = Venue.objects.get(pk=current_access_id)
        elif user_type == 'Organizer':
            current_access = Exhibition.objects.get(pk=current_access_id)
        else:
            current_access = Booth.objects.get(pk=current_access_id)

        # 获取当前场馆的当前楼层的Root SpaceUnit节点(parent_unit=None 且创建时间最早)
        root = current_access.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
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

@csrf_exempt
def add_sublayer(request):
    if request.method == 'POST':
        form = AddLayerForm(request.POST)
        if form.is_valid():
            form.save(commit=True)  # save the form and create the new sublayer
            return JsonResponse({'success': 'The new Sublayer has been successfully added!'}, status=200)
        else:
            return JsonResponse({'error': form.errors}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_layer(request):
    if request.method == 'GET':
        floor = int(request.GET.get('floor', 1))
        user_type = request.GET.get('user_type')
        current_access_id = int(request.GET.get('current_access_id', 0))
        # 验证数据有效性:
        if (floor < 1) or (current_access_id is not None) or (user_type not in ['Manager', 'Organizer', 'Exhibitor']):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        layer_id = int(request.GET.get('layer_id', 0))
        layer = get_object_or_404(SpaceUnit, id=layer_id)
        if user_type == 'Manager':
            current_access = get_object_or_404(Venue, pk=current_access_id)
        elif user_type == 'Organizer':
            current_access = get_object_or_404(Exhibition, pk=current_access_id)
        else:
            current_access = get_object_or_404(Booth, pk=current_access_id)
        root = current_access.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
        if root == layer: # 表明当前SpaceUnit是根节点,不能删除
            return JsonResponse({'error': 'The root SpaceUnit cannot be deleted!'}, status=400)

        def delete_recursive(space_unit):
            # 先递归删除所有子单位
            for child in space_unit.child_units.all():
                delete_recursive(child)
            if not space_unit.available and not space_unit.occupied_units.exists(): # 表明当前SpaceUnit没有被预约使用
                # 删除与此SpaceUnit相关联的所有elements
                space_unit.elements.all().delete()
                # 最后删除SpaceUnit本身
                space_unit.delete()
        # 开始递归删除操作
        delete_recursive(layer)
        # 返回删除成功的信息
        return JsonResponse({'success': 'The unused Layer has been successfully deleted!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def edit_layer(request):
    if request.method == 'POST':
        space_unit_id = request.POST.get('id')
        space_unit = get_object_or_404(SpaceUnit, id=space_unit_id)
        form = EditLayerForm(request.POST, instance=space_unit)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'The Layer has been successfully updated!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def add_element(request):
    pass


def delete_element(request):
    pass


def save_layout(request):
    pass


def add_fake_space_unit(request):  # 用于提供假数据的视图函数,不会在生产环境中使用
    # 定义假数据
    name = "Sub-Sub-Sublayer 2 on floor 1"
    description = "This is a test Space Unit."
    floor = 1
    parent_unit = SpaceUnit.objects.get(pk=16)
    affiliation = Venue.objects.get(pk=6)
    affiliation_content_type = ContentType.objects.get_for_model(Venue)

    # 创建SpaceUnit实例
    space_unit = SpaceUnit.objects.create(
        name=name,
        description=description,
        floor=floor,
        parent_unit=parent_unit,
        available=False,
        affiliation_content_type=affiliation_content_type,
        affiliation_object_id=affiliation.pk
    )

    # 返回新创建的SpaceUnit的信息
    return JsonResponse({
        'id': space_unit.id,
        'name': space_unit.name,
        'description': space_unit.description,
        'floor': space_unit.floor,
        'parent_unit': space_unit.parent_unit.id if space_unit.parent_unit else None,
        'affiliation_type': str(space_unit.affiliation_content_type),
        'affiliation_id': space_unit.affiliation_object_id
    }, safe=False)
