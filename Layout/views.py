from django.shortcuts import render

from Venue.models import Venue


def venue_layout(request):
    # 从session中获取venue_id
    venue_id = request.session.get('venue_id')
    venue = Venue.objects.get(id=venue_id)
    # 获取当前场馆的items
    items = venue.items.all()
    return render(request, 'Layout/venue_layout.html', {'venue': venue, 'items': items})
