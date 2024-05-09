import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

import Inventory.views
from Booth.models import BoothApplication
from Exhibition.models import ExhibitionApplication
from Inventory.models import ResourceApplication, Item
from .forms import RegisterForm, LoginForm, ReplyMessageForm  # 导入注册和登录表单类
from django.contrib.auth import authenticate, login as auth_login  # 导入认证和登录方法
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


def register(request):
    if request.method == 'POST':  # 如果是 POST 请求
        form = RegisterForm(request.POST)  # 使用提交的数据实例化注册表单
        if form.is_valid():  # 如果表单数据有效
            user = form.save()  # 保存用户信息
            user_type = form.cleaned_data.get('account_type')
            if user_type == 'Manager':
                manager = Manager.objects.create(detail=user)
                manager.save()
            elif user_type == 'Organizer':
                organizer = Organizer.objects.create(detail=user)
                organizer.save()
            elif user_type == 'Exhibitor':
                exhibitor = Exhibitor.objects.create(detail=user)
                exhibitor.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('User:login')  # 重定向到登录页面
    else:
        form = RegisterForm()  # 创建一个空的注册表单
    return render(request, 'User/register.html', {'form': form})  # 渲染注册页面，显示空表单


@never_cache  # 禁用缓存，防止用户未退出登录直接通过浏览器返回按钮访问登录页面
def login(request):
    if request.user.is_authenticated:  # 如果用户已经登录
        return redirect('Venue:home')  # 重定向到主页
    if request.method == 'POST':  # 如果是 POST 请求
        form = LoginForm(request.POST)  # 使用提交的数据实例化登录表单
        if form.is_valid():  # 如果表单数据有效
            username = form.cleaned_data.get('username')  # 获取用户名
            password = form.cleaned_data.get('password')  # 获取密码
            user = authenticate(username=username, password=password)  # 调用认证方法验证用户
            if user is not None:  # 如果用户存在
                auth_login(request, user)  # 将用户存入session
                user_type = 'Manager' if hasattr(request.user, 'manager') \
                    else 'Organizer' if hasattr(request.user, 'organizer') \
                    else 'Exhibitor' if hasattr(request.user, 'exhibitor') \
                    else 'Guest'
                request.session['user_type'] = user_type  # 将user_type存入session
                messages.success(request, 'Login successful. Welcome!')
                return redirect('Venue:home')  # 重定向到主页
            else:
                # 如果认证失败，将错误信息返回给用户并重新渲染登录页面
                messages.error(request, 'Invalid login credentials.')
    else:
        form = LoginForm()  # 创建一个空的登录表单
    return render(request, 'User/login.html', {'form': form})  # 渲染登录页面，显示空表单


def logout(request):
    request.session.flush()  # 清空session
    messages.success(request, 'You have been logged out.')
    return redirect('User:login')


def profile(request):
    if request.method == 'GET':  # 如果是 GET 请求
        # 从session中获取当前用户的数据
        user = request.user
        if hasattr(user, 'manager'):
            user_type = 'Manager'
        elif hasattr(user, 'organizer'):
            user_type = 'Organizer'
        else:
            user_type = 'Exhibitor'
        return render(request, 'User/profile.html', {'user': user, 'user_type': user_type})
    else:  # POST请求, 处理用户信息更新
        # 从request中获取用户提交的数据
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 获取当前登录的用户实例
        user = request.user
        # 检查是否提供了有效的用户名，且与当前不同
        if new_username and user.username != new_username:
            if not User.objects.filter(username=new_username).exists():
                user.username = new_username
            else:
                return JsonResponse({'error': 'Username already exists.'}, status=400)

        # 检查是否提供了有效的邮箱，且与当前不同
        if new_email and user.email != new_email:
            if not User.objects.filter(email=new_email).exists():
                user.email = new_email
            else:
                return JsonResponse({'error': 'Email already exists.'}, status=400)

        # 检查是否提供了密码，并进行相应的处理
        if new_password and confirm_password and not check_password(new_password, user.password):
            if new_password == confirm_password:
                user.set_password(new_password)
                # 更新session以避免用户被登出
                update_session_auth_hash(request, user)
            else:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)
        # 保存用户信息的更改
        user.save()
        # 返回更新后的用户信息页
        return JsonResponse({'message': 'Profile updated successfully.'}, status=200)


@login_required
def view_message(request):
    try:
        # 消息类型默认为 'unread', 申请类型默认为 'exhibition'
        item_type = request.GET.get('item_type', 'unread')
        applications_type = request.GET.get('applications_type', 'exhibition')
        # 根据请求的消息类型进行查询
        if item_type == 'unread':
            items = Message.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
        elif item_type == 'inbox':
            items = Message.objects.filter(recipient=request.user).order_by('-created_at')
        elif item_type == 'sent':
            items = Message.objects.filter(sender=request.user).order_by('-created_at')
        # 根据请求的申请类型进行查询
        elif item_type == 'applications':
            if applications_type == 'exhibition':
                if hasattr(request.user, 'manager'):
                    items = ExhibitionApplication.objects.all().order_by('exhibition__start_at')
                elif hasattr(request.user, 'organizer'):
                    items = ExhibitionApplication.objects.filter(applicant=request.user).order_by(
                        'exhibition__start_at')
                else:
                    raise Http404("Permission denied")
            elif applications_type == 'booth':
                if hasattr(request.user, 'manager'):
                    items = BoothApplication.objects.all().order_by('booth__start_at')
                elif hasattr(request.user, 'exhibitor'):
                    items = BoothApplication.objects.filter(applicant=request.user).order_by('booth__start_at')
                else:
                    raise Http404("Permission denied")
            elif applications_type == 'resource':
                if hasattr(request.user, 'manager'):
                    items = ResourceApplication.objects.all().order_by('booth__start_at')
                elif hasattr(request.user, 'exhibitor'):
                    items = ResourceApplication.objects.filter(applicant=request.user).order_by('booth__start_at')
                else:
                    raise Http404("Permission denied")
            else:
                raise Http404("Application type not found")
        else:
            raise Http404("Message type not found")
        # 设置分页
        paginator = Paginator(items, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 自定义侧边栏链接
        custom_items = [
            {'name': '🚨 Unread', 'url': '?item_type=unread',
             'active_class': 'active' if item_type == 'unread' else ''},
            {'name': '📭 Inbox', 'url': '?item_type=inbox',
             'active_class': 'active' if item_type == 'inbox' else ''},
            {'name': '🗳️ Sent', 'url': '?item_type=sent',
             'active_class': 'active' if item_type == 'sent' else ''},
            {'name': '📝 Applications', 'url': '?item_type=applications',
             'active_class': 'active' if item_type == 'applications' else ''},
        ]

        message_form = ReplyMessageForm()
        user_type = request.session.get('user_type')
        return render(request, 'User/message.html',
                      {
                          'page_obj': page_obj,  # 传递分页对象
                          'show_sidebar': True,  # 显示侧边栏
                          'page_title': 'Message Center',  # 侧栏标题
                          'item_type': item_type,  # 将当前消息类型传递到模板中，用于侧边栏链接
                          'applications_type': applications_type,  # 传递申请类型
                          'custom_items': custom_items,  # 传递自定义侧边栏链接
                          'message_form': message_form,  # 传递回复消息表单
                          'user_type': user_type  # 传递用户类型
                      })
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


@login_required
def view_message_detail(request, message_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        message = Message.objects.get(id=message_id)
        message_detail = message.detail

        # 如果消息的接收者是当前用户且消息未读，则将消息标记为已读
        if message.recipient == request.user and not message.is_read:
            message.is_read = True
            message.save()

        # 添加关联申请
        application_id = message_detail.application_object_id
        related_messages_data = []
        if application_id:
            # 获取与应用程序关联的所有消息详细信息，并按消息创建时间降序排序
            related_messages_detail = MessageDetail.objects.filter(
                application_object_id=application_id,
                application_content_type=message_detail.application_content_type,
                message__created_at__lt=message.created_at  # 只返回创建时间在当前消息之前的消息
            ).order_by('-message__created_at')

            # 将关联消息转换为 JSON 数据
            for related_message_detail in related_messages_detail:
                related_message = related_message_detail.message
                related_messages_data.append({
                    'title': related_message.title,
                    'sender': related_message.sender.username,
                    'recipient': related_message.recipient.username,
                    'created_at': related_message.created_at.strftime('%Y-%m-%d %H:%M'),
                    'content': related_message_detail.content,
                })

        data = {
            'title': message.title,
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
            'content': message_detail.content,
            'application_id': application_id,
            'application_type': str(message_detail.application_content_type.model).replace('application', '')
            if message_detail.application_content_type else '',
            'related_messages': related_messages_data,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


@login_required
def view_application_detail(request, application_type, application_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        if application_type == 'exhibition':
            application = ExhibitionApplication.objects.get(id=application_id)
            location = application.exhibition.venue.name + ' >>'
            for sector in application.exhibition.sectors.all():
                location += ' ' + sector.name
            data = {
                'application_type': application_type,
                'title': "Application for Exhibition '" + application.exhibition.name + "'",
                'image_url': application.exhibition.image.url if application.exhibition.image else '',
                'description': application.description,
                'applicant': application.applicant.username,
                'start_at': application.exhibition.start_at.strftime('%Y-%m-%d %H:%M'),
                'end_at': application.exhibition.end_at.strftime('%Y-%m-%d %H:%M'),
                'location': location,
                'stage': application.get_stage_display(),
            }
        elif application_type == 'booth':
            application = BoothApplication.objects.get(id=application_id)
            print(1)
            location = application.booth.exhibition.venue.name + ' >>'
            for sector in application.booth.sectors.all():
                location += ' ' + sector.name
            data = {
                'application_type': application_type,
                'title': "Application for Booth '" + application.booth.name + "' at Exhibition '" + application.booth.exhibition.name + "'",
                'image_url': application.booth.image.url if application.booth.image else '',
                'applicant': application.applicant.username,
                'start_at': application.booth.start_at.strftime('%Y-%m-%d %H:%M'),
                'end_at': application.booth.end_at.strftime('%Y-%m-%d %H:%M'),
                'description': application.description,
                'location': location,
                'stage': application.get_stage_display(),
            }
        elif application_type == 'resource':
            application = ResourceApplication.objects.get(id=application_id)
            data = {
                'application_type': 'resource',
                'title': "Booth '" + application.booth.name + "' Apply for " + application.category.name,
                'image_url': application.category.image.url if application.category.image else '',
                'applicant': application.applicant.username,
                'start_at': application.booth.start_at.strftime('%Y-%m-%d %H:%M'),
                'end_at': application.booth.end_at.strftime('%Y-%m-%d %H:%M'),
                'quantity': application.quantity,
                'stage': application.get_stage_display(),
            }
        else:
            return JsonResponse({'error': 'Application type not found'}, status=404)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


@login_required
def reply_message(request, message_id):
    if request.method == 'POST':
        try:
            # 从请求体加载JSON数据
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            if not title or not content:
                return JsonResponse({'error': 'You cannot send something without writing it!'}, status=400)

            # 获取消息关联的申请
            message = Message.objects.get(id=message_id)
            message_detail = message.detail
            # 如果消息关联了申请，则将回复消息也关联到申请
            if message_detail.application_object_id is not None:
                application = message_detail.application
                if application.stage != Application.Stage.INITIAL_SUBMISSION:
                    return JsonResponse({'error': 'Application has been processed.'}, status=200)
                application_type = ContentType.objects.get_for_model(application)
                new_message = Message.objects.create(title=title, sender=request.user, recipient=message.sender)
                new_message_detail = MessageDetail.objects.create(message=new_message, content=content,
                                                                  application_object_id=application.id,
                                                                  application_content_type=application_type)
                new_message.detail = new_message_detail
                new_message.save()
            else:  # 无关联申请的消息
                new_message = Message.objects.create(title=title, sender=request.user, recipient=message.sender)
                new_message_detail = MessageDetail.objects.create(message=new_message, content=content)
                new_message.detail = new_message_detail
                new_message.save()
            return JsonResponse({'success': 'Reply sent successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def reject_application(request, application_type, application_id):
    if request.method == 'POST':
        if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        try:
            # 获取申请实例
            if application_type == 'exhibition':
                application = ExhibitionApplication.objects.get(id=application_id)
                content = 'Sorry, your application ' + application.exhibition.name + ' has been rejected.'
            elif application_type == 'booth':
                application = BoothApplication.objects.get(id=application_id)
                content = 'Sorry, your application for ' + application.booth.name + ' has been rejected.'
            elif application_type == 'resource':
                application = ResourceApplication.objects.get(id=application_id)
                content = 'Sorry, your application for ' + application.category.name + ' has been rejected.'
            else:
                return JsonResponse({'error': 'Application type not found'}, status=404)

            # 通过申请
            if application.stage != Application.Stage.INITIAL_SUBMISSION:
                return JsonResponse({'error': 'Application has been processed.'}, status=200)
            application.stage = Application.Stage.REJECTED
            application.save()

            # 发送拒绝消息
            application_content_type = ContentType.objects.get_for_model(application)
            new_message = Message.objects.create(title=application_type.capitalize() + ' Application Rejected',
                                                 sender=request.user, recipient=application.applicant)
            new_message_detail = MessageDetail.objects.create(message=new_message,
                                                              content=content,
                                                              application_object_id=application.id,
                                                              application_content_type=application_content_type)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Application rejected successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def accept_application(request, application_type, application_id):
    if request.method == 'POST':
        if not hasattr(request.user, 'manager'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        try:
            # 获取申请实例
            if application_type == 'exhibition':
                application = ExhibitionApplication.objects.get(id=application_id)
                content = 'Congratulations! Your application ' + application.exhibition.name + ' has been accepted.'
            elif application_type == 'booth':
                application = BoothApplication.objects.get(id=application_id)
                content = 'Congratulations! Your application for ' + application.booth.name + ' has been accepted.'
            elif application_type == 'resource':
                application = ResourceApplication.objects.get(id=application_id)
                content = 'Congratulations! Your application for ' + application.category.name + ' has been accepted.'
            else:
                return JsonResponse({'error': 'Application type not found'}, status=404)

            # 通过申请
            if application.stage != Application.Stage.INITIAL_SUBMISSION:
                return JsonResponse({'error': 'Application has been processed.'}, status=200)
            application.stage = Application.Stage.ACCEPTED
            application.save()
            if application_type == 'resource':
                rent_item = Item.objects.filter(category=application.category, is_using=False, is_damaged=False).first()
                if rent_item:
                    rent_item.affiliation_content_type = ContentType.objects.get_for_model(application.booth)
                    rent_item.affiliation_object_id = application.booth.id
                else:
                    return JsonResponse({'error': 'No available item found.'}, status=404)

            # 发送接受消息
            application_content_type = ContentType.objects.get_for_model(application)
            new_message = Message.objects.create(title=application_type.capitalize() + ' Application Accepted',
                                                 sender=request.user, recipient=application.applicant)
            new_message_detail = MessageDetail.objects.create(message=new_message,
                                                              content=content,
                                                              application_object_id=application.id,
                                                              application_content_type=application_content_type)
            new_message.detail = new_message_detail
            new_message.save()
            return JsonResponse({'success': 'Application accepted successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

# TODO 资源重名提示
# 创建资源Public属性非管理员不可选
