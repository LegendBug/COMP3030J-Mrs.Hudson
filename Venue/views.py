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
            return JsonResponse({'errors': form.errors}, status=400)


def venue(request, venue_id):
    current_venue = Venue.objects.filter(id=venue_id).first()
    if current_venue is None:
        return redirect('Venue:home')
    request.session['venue_id'] = venue_id  # 将venue_id存入session

    user = request.user
    user_type = 'Manager' if hasattr(request.user, 'manager') \
        else 'Organizer' if hasattr(request.user, 'organizer') \
        else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
        else 'Guest'
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
