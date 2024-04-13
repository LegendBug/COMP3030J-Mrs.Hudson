from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm  # 导入注册和登录表单类
from django.contrib.auth import authenticate, login as auth_login  # 导入认证和登录方法
from .models import *


def index(request):
    if request.user.is_authenticated:
        return redirect('User:home')
    else:
        return redirect('User:login')


def home(request):
    if not request.user.is_authenticated:
        return redirect('User:login')
    return render(request, 'User/home.html')


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
            return redirect('User:login')  # 重定向到登录页面
        else:
            # 如果表单数据无效，将错误信息返回给用户并重新渲染注册页面
            return render(request, 'User/register.html', {'form': form})
    else:
        form = RegisterForm()  # 创建一个空的注册表单
        return render(request, 'User/register.html', {'form': form})  # 渲染注册页面，显示空表单


@never_cache  # 禁用缓存，防止用户未退出登录直接通过浏览器返回按钮访问登录页面
def login(request):
    # 检查用户是否已登录
    if request.user.is_authenticated:
        return redirect('User:home')

    if request.method == 'POST':  # 如果是 POST 请求
        form = LoginForm(request.POST)  # 使用提交的数据实例化登录表单
        if form.is_valid():  # 如果表单数据有效
            username = form.cleaned_data.get('username')  # 获取用户名
            password = form.cleaned_data.get('password')  # 获取密码
            user = authenticate(username=username, password=password)  # 调用认证方法验证用户
            if user is not None:  # 如果用户存在
                auth_login(request, user)  # 将用户存入session
                # request.session['logged_in'] = True  # 将登录状态存入session(便于模板中判断用户是否登录)
                return redirect('User:home')  # 重定向到主页
            else:
                # 如果认证失败，将错误信息返回给用户并重新渲染登录页面
                return render(request, 'User/login.html', {'form': form})
        else:
            # 如果表单数据无效，将错误信息返回给用户并重新渲染登录页面
            return render(request, 'User/login.html', {'form': form})
    else:
        form = LoginForm()  # 创建一个空的登录表单
        return render(request, 'User/login.html', {'form': form})  # 渲染登录页面，显示空表单


def logout(request):
    request.session.flush()
    return redirect('User:login')


# 跳转到消息页面
def view_message(request):
    if not request.user.is_authenticated:
        return redirect('User:login')

    try:
        # 消息类型默认为 'unread_message'
        message_type = request.GET.get('type', 'unread_messages')
        # 根据请求的消息类型进行查询
        if message_type == 'unread_messages':
            messages = Message.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
        elif message_type == 'all_messages':
            messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
        elif message_type == 'sent_messages':
            messages = Message.objects.filter(sender=request.user).order_by('-created_at')
        else:
            raise Http404("Message type not found")

        # 设置分页
        paginator = Paginator(messages, 10)  # 每页显示 10 条消息
        page_number = request.GET.get('page')  # 获取页码参数（默认为第一页）
        page_obj = paginator.get_page(page_number)  # 获取当前页的消息

        # 创建包含每个消息详细信息页面URL的字典
        message_urls = {message.id: reverse('User:view_message_detail', args=[message.id]) for message in page_obj}
        return render(request, 'User/message.html',
                      {'page_obj': page_obj,
                       'message_type': message_type,  # 将当前消息类型传递到模板中，用于侧边栏链接
                       'message_urls': message_urls
                       })
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


def view_message_detail(request, message_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        message = Message.objects.get(id=message_id)
        message_detail = message.detail



        if not message.is_read:
            message.is_read = True
            message.save()
        data = {
            'title': message.title,
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': message_detail.content,
            'application': message_detail.application if hasattr(message_detail, 'application') else None,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)

