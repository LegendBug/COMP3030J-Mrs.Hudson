from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import Manager, Organizer, Exhibitor  # 根据你的模型调整
from django.http import HttpResponse


def register(request):
    if request.method == 'GET':
        return render(request, 'User/register.html')
    elif request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')  # 获取用户类型

        # 这里可以添加更多的验证逻辑
        if not username or not password or not email or not user_type:
            return HttpResponse("Invalid input.", status=400)

        # 根据用户类型创建不同的用户实例
        if user_type == 'Manager':
            new_user = Manager(username=username, password=make_password(password), email=email)
        elif user_type == 'Organizer':
            new_user = Organizer(username=username, password=make_password(password), email=email)
        elif user_type == 'Exhibitor':
            new_user = Exhibitor(username=username, password=make_password(password), email=email)
        else:
            return HttpResponse("Invalid user type.", status=400)

        new_user.save()
        # 重定向到登录页面或其他页面
        return redirect('/login')  # 调整为合适的重定向地址

    # 对于其他 HTTP 方法，返回错误或适当的响应
    return HttpResponse("Invalid HTTP method.", status=405)

def login(request):
    if request.method == 'GET':
        return render(request, 'User/login.html')
    elif request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')  # 获取用户类型

        # 这里可以添加更多的验证逻辑
        if not username or not password or not user_type:
            return HttpResponse("Invalid input.", status=400)

        # 根据用户类型查询用户实例
        if user_type == 'Manager':
            user = Manager.objects.filter(username=username).first()
        elif user_type == 'Organizer':
            user = Organizer.objects.filter(username=username).first()
        elif user_type == 'Exhibitor':
            user = Exhibitor.objects.filter(username=username).first()
        else:
            return HttpResponse("Invalid user type.", status=400)

        if user is None:
            return HttpResponse("User not found.", status=404)

        # 验证密码
        if not user.check_password(password):
            return HttpResponse("Incorrect password.", status=401)

        # 登录成功，可以设置 session 或 cookie
        return HttpResponse("Login success.", status=200)

    # 对于其他 HTTP 方法，返回错误或适当的响应
    return HttpResponse("Invalid HTTP method.", status=405)