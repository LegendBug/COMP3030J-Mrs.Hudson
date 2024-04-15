import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render

from Exhibition.models import Exhibition, ExhibitionApplication
from Layout.models import SpaceUnit
from User.models import Message, MessageDetail, Organizer, Manager
from Venue.models import Venue


# 创建展览申请
def create_exhib_application(request):
    if request.method == 'POST':
        try:
            venue_id = request.POST.get('venue_id')

            name = request.POST.get('name')
            description = request.POST.get('description')
            start_at = timezone.make_aware(datetime.datetime.strptime(request.POST.get('start_at'), '%Y-%m-%d'))
            end_at = timezone.make_aware(datetime.datetime.strptime(request.POST.get('end_at'), '%Y-%m-%d'))
            image = request.FILES.get('image')
            sectors = request.POST.get('sectors')
            content = request.POST.get('content')

            if not all([venue_id, name, description, start_at, end_at, image, sectors]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            venue = Venue.objects.get(pk=venue_id)
            organizer = Organizer.objects.get(detail=request.user)
            spaceUnit = SpaceUnit.objects.get(id=sectors)  # 确保sectors是正确的SpaceUnit ID

            new_exhibition = Exhibition.objects.create(
                name=name, description=description, start_at=start_at, end_at=end_at,
                image=image, organizer=organizer, venue=venue, sectors=spaceUnit
            )
            if not new_exhibition:
                return JsonResponse({'error': 'Failed to create exhibition'}, status=500)
            new_exhib_application = ExhibitionApplication.objects.create(applicant=request.user,
                                                                         description=description,
                                                                         exhibition=new_exhibition)
            if not new_exhib_application:
                return JsonResponse({'error': 'Failed to create exhibition application'}, status=500)
            new_exhibition.application = new_exhib_application
            new_exhibition.save()
            new_exhib_application.save()
            # 创建提示消息和消息详情
            new_message = Message.objects.create(title='New Exhibition Application for ' + name, sender=request.user,
                                                 recipient=Manager.objects.first().detail)
            application_type = ContentType.objects.get_for_model(new_exhib_application)
            new_message_detail = MessageDetail.objects.create(message=new_message, content=content,
                                                              application_id=new_exhib_application.id,
                                                              application_type=application_type)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Exhibition application created successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
