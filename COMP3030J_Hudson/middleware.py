from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 允许特定路由不通过登录验证，例如登录页
        allowed_paths = [reverse('User:login'), reverse('User:register'), reverse('Venue:home'), reverse('User:welcome')]
        if request.path.startswith(settings.MEDIA_URL) or request.path in allowed_paths:
            return self.get_response(request)

        if not request.user.is_authenticated:  # 用户未登录
            return redirect('User:login')  # 重定向到登录页面

        response = self.get_response(request)
        return response
