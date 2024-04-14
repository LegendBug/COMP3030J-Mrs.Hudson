from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from Venue.form import VenueForm
from Venue.models import Venue
from django.contrib import messages


@require_http_methods(["GET", "POST"])
def home(request):
    if request.method == 'GET':
        # GET请求，展示场馆列表和空的创建表单
        venues = Venue.objects.all()
        form = VenueForm()  # 创建一个空的表单实例
        is_manager = False
        if request.user.is_authenticated and hasattr(request.user, 'manager'):
            is_manager = True
        return render(request, 'Venue/home.html', {'venues': venues, 'is_manager': is_manager, 'form': form})
    else:  # POST请求
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'errors': 'Permission denied!'}, status=403)
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue created successfully!')
            # TODO 该消息无法显示,需要debug
            return redirect('Venue:home')
        else:
            return JsonResponse({'errors': form.errors}, status=400)

def venue(request):
    venues = Venue.objects.all()
    floors = Venue.objects.values_list('floor', flat=True).distinct()
    areas = Venue.objects.values_list('area', flat=True).distinct()

    # 通过GET请求参数筛选场馆
    # status_para = request.GET.get('status')
    address_para = request.GET.get('address')
    area_para = request.GET.get('area')
    floor_para = request.GET.get('floor')
    name_input = request.GET.get('name')

    if address_para and address_para != '':
        venues = venues.filter(address=address_para)
    if area_para and area_para != '':
        venues = venues.filter(area=area_para)
    if floor_para and floor_para != '':
        venues = venues.filter(floor=floor_para)
    if name_input and name_input != '':
        venues = venues.filter(name__icontains=name_input)

    return render(request, 'Venue/venue.html', {'venues': venues, 'floors': floors, 'areas': areas})