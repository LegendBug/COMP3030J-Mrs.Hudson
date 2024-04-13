from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 允许特定路由不通过登录验证，例如登录页
        if request.path in [reverse('User:login'), reverse('User:register')]: # 如果用户请求的路径是登录或注册页面,则放行
            return self.get_response(request)

        if not request.user.is_authenticated:  # 用户未登录
            return redirect('User:login')  # 重定向到登录页面

        response = self.get_response(request)
        return response
