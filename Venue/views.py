from django.http import JsonResponse
from django.shortcuts import render, redirect

from Exhibition.forms import ExhibApplicationForm, FilterExhibitionsForm
from Venue.forms import CreateVenueForm
from Venue.models import Venue
from Exhibition.models import Exhibition
from django.contrib import messages


def home(request):
    if request.method == 'GET':
        # GET请求，展示场馆列表和空的创建表单
        venues = Venue.objects.all()
        form = CreateVenueForm()  # 创建一个空的表单实例
        return render(request, 'Venue/home.html',
                      {'venues': venues, 'user_type': request.session.get('user_type', 'Guest'),
                       'messages': messages.get_messages(request),
                       'form': form})
    else:  # POST请求
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'errors': 'Permission denied!'}, status=403)
        form = CreateVenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue created successfully!'})
        else:
            # {"name": [{"message": "This field is required.", "code": "required"}], "address": [{"message": "This field is required.", "code": "required"}], "floor": [{"message": "This field is required.", "code": "required"}], "image": [{"message": "This field is required.", "code": "required"}]}
            return JsonResponse({'errors': form.errors.as_json()}, status=400) #TODO 此处前端没有遍历errors,导致报错消息无法显示


def venue(request, venue_id):
    current_venue = Venue.objects.filter(id=venue_id).first()
    if current_venue is None:
        return redirect('Venue:home')
    request.session['venue_id'] = venue_id  # 将venue_id存入session

    user = request.user
    user_type = request.session.get('user_type', 'Manager')
    exhibitions = None

    if request.method == 'GET':
        # 根据用户类型筛选展览信息
        if user not in [None, ''] and hasattr(user, 'manager'):
            exhibitions = current_venue.exhibitions.all()
        elif user not in [None, ''] and hasattr(user, 'organizer'):
            exhibitions = current_venue.exhibitions.filter(organizer=user.organizer)
        elif user not in [None, ''] and hasattr(user, 'exhibitor'):
            current_exhibitions = current_venue.exhibitions.all()
            booths = user.exhibitor.booths
            exhibitions = []
            for booth in booths:
                if booth.exhibition in current_exhibitions:
                    exhibitions.append(booth.exhibition)
        else:  # 游客
            exhibitions = current_venue.exhibitions.all()
    elif request.method == 'POST':
        submitted_filter_form = FilterExhibitionsForm(request.POST)
        if submitted_filter_form.is_valid():
            exhibitions = submitted_filter_form.filter()
            messages.success(request, 'Filter exhibitions success!')
        else:
            exhibitions = Exhibition.objects.none()
            # messages.error(request, 'Filter exhibitions failed! Please check the form.')
    application_form = ExhibApplicationForm()
    filter_form = FilterExhibitionsForm()
    return render(request, 'Venue/venue.html', {
        'exhibitions': exhibitions,
        'venue': current_venue,
        'user_type': user_type,
        'application_form': application_form,
        'filter_form': filter_form
    })


def modify_venue(request, venue_id):
    if request.method == 'GET':
        venue = Venue.objects.filter(id=venue_id).first()
        if venue is None:
            return redirect('Venue:home')
        form = CreateVenueForm(instance=venue)
        return render(request, 'Venue/modify_venue.html', {'form': form})
    else:
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'errors': 'Permission denied!'}, status=403)
        venue = Venue.objects.filter(id=venue_id).first()
        if venue is None:
            return JsonResponse({'errors': 'Venue not found!'}, status=404)
        form = CreateVenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Venue modified successfully!'})
        else:
            return JsonResponse({'errors': form.errors.as_json()}, status=400)


def delete_venue(request, venue_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
        return JsonResponse({'errors': 'Permission denied!'}, status=403)
    venue = Venue.objects.filter(id=venue_id).first()
    if venue is None:
        return JsonResponse({'errors': 'Venue not found!'}, status=404)
    venue.delete()
    return JsonResponse({'success': 'Venue deleted successfully!'})