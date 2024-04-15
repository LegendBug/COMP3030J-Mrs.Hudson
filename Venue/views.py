from django.http import JsonResponse
from django.shortcuts import render, redirect
from Venue.form import VenueForm
from Venue.models import Venue
from Exhibition.models import Exhibition
from django.contrib import messages


def home(request):
    if request.method == 'GET':
        # GET请求，展示场馆列表和空的创建表单
        venues = Venue.objects.all()
        form = VenueForm()  # 创建一个空的表单实例
        is_manager = False
        if request.user.is_authenticated and hasattr(request.user, 'manager'):
            is_manager = True
        return render(request, 'Venue/home.html',
                      {'venues': venues, 'is_manager': is_manager, 'messages': messages.get_messages(request),
                       'form': form})
    else:  # POST请求
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'errors': 'Permission denied!'}, status=403)
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue created successfully!'})
        else:
            return JsonResponse({'errors': form.errors}, status=400)


def venue(request):
    exhibitions = Exhibition.objects.all()

    sectors = Exhibition.objects.values_list('sectors', flat=True).distinct()
    start_ats = Exhibition.objects.values_list('start_at', flat=True).distinct()
    end_ats = Exhibition.objects.values_list('end_at', flat=True).distinct()
    organizers = Exhibition.objects.values_list('organizer', flat=True).distinct()

    # filter exhibitions via GET parameters
    sectors_param = request.GET.get('sectors')
    start_ats_param = request.GET.get('start_ats')  # FIXME need to convert the string to datetime
    end_ats_param = request.GET.get('end_ats')  # FIXME need to convert the string to datetime
    organizers_param = request.GET.get('organizers')
    name_input = request.GET.get('name')

    if sectors_param and sectors_param != '':
        exhibitions = exhibitions.filter(sectors=sectors_param)
    if start_ats_param and start_ats_param != '':
        exhibitions = exhibitions.filter(start_at=start_ats_param)
    if end_ats_param and end_ats_param != '':
        exhibitions = exhibitions.filter(end_at=end_ats_param)
    if organizers_param and organizers_param != '':
        exhibitions = exhibitions.filter(organizer=organizers_param)
    if name_input and name_input != '':
        exhibitions = exhibitions.filter(name__icontains=name_input)

    return render(request, 'Venue/venue.html',
                  {'exhibitions': exhibitions, 'sectors': sectors, 'start_ats': start_ats, 'end_ats': end_ats,
                   'organizers': organizers})
