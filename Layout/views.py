from django.shortcuts import render
from rest_framework import status
from Venue.models import Venue
from django.http import JsonResponse
from .serializers import *


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
    return render(request, 'Layout/venue_layout.html',
                  {'venue': venue, 'items': items, 'user_type': user_type, 'floor_range': range(1, venue.floor)})


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
    return render(request, 'Layout/layout.html',
                  {'venue': venue, 'user_type': user_type, 'items': items, 'floor_range': range(1, venue.floor + 1)})


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


def create_sublayer(request):  # {% static 'Layout: create_sublayer' %}
    # 从JSON数据中获取父SpaceUnit的ID
    parent_id = request.POST.get('parent_id')
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')

    pass


def delete_layer(request):
    pass


def add_element(request):
    pass


def delete_element(request):
    pass


def save_layout(request):
    pass
