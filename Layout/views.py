from django.shortcuts import render
from rest_framework import status
from Venue.models import Venue
from django.http import JsonResponse
from .forms import AddLayerForm
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType


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
    return render(request, 'Layout/layout.html',
                  {'venue': venue, 'user_type': user_type, 'items': items, 'floor_range': range(1, venue.floor + 1),
                   'add_sublayer_form': add_sublayer_form})


def synchronize_data(request):  # {url (Layout:get_floor_data)}
    # 从GET请求中获取当前的floor
    floor = int(request.GET.get('floor', "1"))
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    # 获取当前场馆的当前楼层的Root SpaceUnit节点(parent_unit=None 且创建时间最早)
    root = venue.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
    # 返回JSON化的root数据
    if root is not None:
        # 使用Serializer序列化root
        serializer = SpaceUnitSerializer(root)
        return JsonResponse(serializer.data)  # 使用Django的JsonResponse返回数据
    else:
        return JsonResponse({'error': 'No root SpaceUnit found for the specified floor'},
                            status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def add_sublayer(request):
    if request.method == 'POST':
        form = AddLayerForm(request.POST)
        if form.is_valid():
            new_sublayer = form.save(commit=True)  # save the form and create the new sublayer
            venue_id = new_sublayer.affiliation_object_id
            venue = Venue.objects.get(id=venue_id)
            floor = new_sublayer.floor
            root = venue.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
            serializer = SpaceUnitSerializer(root)
            return JsonResponse(serializer.data, safe=False)
        else:
            print(form.errors)
            return JsonResponse({'error': form.errors}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_layer(request):
    pass


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
