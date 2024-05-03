import datetime

from django.contrib.contenttypes.models import ContentType

from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from Booth.models import Booth
from Exhibition.forms import ExhibApplicationForm
from Exhibition.models import Exhibition, ExhibitionApplication
from User.models import Message, MessageDetail, Organizer, Manager, Exhibitor
from Venue.models import Venue


def exhibition(request, exhibition_id):
    current_exhibition = Exhibition.objects.filter(id=exhibition_id).first()
    if current_exhibition is None:
        venue_id = request.session.get('venue_id', None)
        if venue_id:
            return redirect('Venue:venue', venue_id=venue_id)
        else:
            return redirect('Venue:home')
    request.session['exhibition_id'] = exhibition_id  # 将exhibition_id存入session

    user = request.user
    user_type = request.session.get('user_type', 'Manager')
    items = None

    if request.method == 'GET':
        # 根据用户类型筛选展览信息
        if user not in [None, ''] and not hasattr(user, 'exhibitor'):
            booths = current_exhibition.booths.all()
        else:  # 参展方
            booths = Exhibitor.objects.filter(detail_id=user.id).first().booths
        return render(request, 'Exhibition/exhibition.html', {'exhibition': current_exhibition, 'booths': booths})
    else:
        return HttpResponseNotAllowed(['GET'])


# 创建展览申请
def create_exhibit_application(request):
    if request.method == 'POST':
        try:
            # 获取POST请求中的数据
            print('create')
            form = ExhibApplicationForm(request.POST, request.FILES)
            if not form.is_valid():
                # 获取第一个错误信息
                first_error_key, first_error_messages = list(form.errors.items())[0]
                first_error_message = first_error_key + ': ' + first_error_messages[0]
                return JsonResponse({'error': first_error_message}, status=400)
            venue_id = form.cleaned_data.get('venue_id')
            name = form.cleaned_data.get('exhib_name')
            description = form.cleaned_data.get('exhib_description')
            start_at = form.cleaned_data.get('exhib_start_at')
            end_at = form.cleaned_data.get('exhib_end_at')
            image = form.cleaned_data.get('exhib_image')
            sectors = form.cleaned_data.get('exhib_sectors')
            content = form.cleaned_data.get('message_content')

            print(len(sectors))
            for sector in sectors:
                print(sector.name)
                print(sector.affiliation_object_id)
                print(sector.affiliation_content_type)

            print('end')

            # 创建新的展览和展览申请
            venue = Venue.objects.get(pk=venue_id)
            organizer = Organizer.objects.get(detail=request.user)
            new_exhibition = Exhibition.objects.create(
                name=name, description=description, start_at=start_at, end_at=end_at,
                image=image, organizer=organizer, venue=venue
            )
            new_exhibition.sectors.set(sectors)  # 反向关系需要使用set方法
            new_exhib_application = ExhibitionApplication.objects.create(applicant=request.user,
                                                                         description=description,
                                                                         exhibition=new_exhibition)
            new_exhibition.application = new_exhib_application
            new_exhibition.save()
            new_exhib_application.save()
            # 创建提示消息和消息详情
            new_message = Message.objects.create(title='New Exhibition Application for ' + name, sender=request.user,
                                                 recipient=Manager.objects.first().detail)
            application_type = ContentType.objects.get_for_model(new_exhib_application)
            new_message_detail = MessageDetail.objects.create(message=new_message, content=content,
                                                              application_object_id=new_exhib_application.id,
                                                              application_content_type=application_type)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Exhibition application created successfully!'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
