from django.shortcuts import render
from Venue.models import Venue


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
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'

    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    # 获取当前场馆的items
    items = venue.items.all()
    return render(request, 'Layout/layout.html', {'venue': venue, 'items': items, 'user_type': user_type})

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




