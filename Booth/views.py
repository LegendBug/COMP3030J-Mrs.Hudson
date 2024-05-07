from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render

from Booth.forms import BoothApplicationForm
from Booth.models import Booth, BoothApplication
from Exhibition.models import Exhibition
from User.models import Exhibitor, Message, Manager, MessageDetail


@login_required
def booth(request, booth_id):
    current_booth = Booth.objects.filter(id=booth_id).first()
    if current_booth is None:
        exhibition_id = request.session.get('exhibition_id', None)
        if exhibition_id:
            return redirect('Exhibition:exhibition', exhibition_id=exhibition_id)
        else:
            return redirect('Venue:home')
    request.session['booth_id'] = booth_id  # 将booth_id存入session

    if request.method == 'GET':
        return render(request, 'Booth/booth.html', {'booth': current_booth})
    else:
        return HttpResponseNotAllowed(['GET'])


@login_required
def create_booth_application(request):
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'exhibitor'):
                return JsonResponse({'error': 'Permission denied!'}, status=403)
            # 获取POST请求中的数据
            form = BoothApplicationForm(request.POST, request.FILES)
            if not form.is_valid():
                # 获取第一个错误信息
                first_error_key, first_error_messages = list(form.errors.items())[0]
                first_error_message = first_error_key + ': ' + first_error_messages[0]
                return JsonResponse({'error': first_error_message}, status=400)
            exhibition_id = form.cleaned_data.get('exhib_id')
            name = form.cleaned_data.get('booth_name')
            description = form.cleaned_data.get('booth_description')
            image = form.cleaned_data.get('booth_image')
            sector = form.cleaned_data.get('booth_sector')
            message_content = form.cleaned_data.get('message_content')

            # 创建新的展台和展台申请
            print(exhibition_id)
            exhibition = Exhibition.objects.get(id=exhibition_id)
            exhibitor = Exhibitor.objects.get(detail=request.user)
            new_booth = Booth.objects.create(name=name, description=description, image=image,
                                             exhibitor=exhibitor, exhibition=exhibition,
                                             start_at=exhibition.start_at,
                                             end_at=exhibition.end_at)  # 展台的开始时间和结束时间与展览一致
            new_booth.sectors.set([sector])
            new_booth_application = BoothApplication.objects.create(applicant=request.user,
                                                                    description=description,
                                                                    booth=new_booth)
            new_booth.booth_application = new_booth_application
            new_booth.save()
            new_booth_application.save()
            # 创建提示消息和消息详情
            new_message = Message.objects.create(
                title="New Booth Application for '" + exhibition.name + ': ' + name + "'",
                sender=request.user, recipient=Manager.objects.first().detail)
            application_type = ContentType.objects.get_for_model(new_booth_application)
            new_message_detail = MessageDetail.objects.create(message=new_message, content=message_content,
                                                              application_content_type=application_type,
                                                              application_object_id=new_booth_application.id)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Booth application created successfully!'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Internal server error!', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
