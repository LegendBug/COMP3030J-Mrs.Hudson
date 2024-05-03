from django.shortcuts import render
from Venue.models import Venue
from django.http import JsonResponse

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
    return render(request, 'Layout/venue_layout.html', {'venue': venue, 'items': items, 'user_type': user_type})


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
                  {'venue': venue, 'user_type': user_type, 'items': items})


def get_floor_data(request): # {url (Layout:get_floor_data)}
    # 从GET请求中获取当前的floor
    floor = int(request.GET.get('floor', "1"))
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    # 获取当前场馆的当前楼层的Root SpaceUnit节点(parent_unit=None 且创建时间最早)
    root = venue.sectors.filter(floor=floor, parent_unit=None).order_by('created_at').first()
    # 返回JSON化的root数据
    return JsonResponse(root.to_dict())


def add_layer(request):
    pass


def delete_layer(request):
    pass


def add_element(request):
    pass


def delete_element(request):
    pass


def save_layout(request):
    pass
