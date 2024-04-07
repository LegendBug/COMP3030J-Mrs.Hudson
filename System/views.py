from django.shortcuts import render, redirect


# 当settings.py的DEBUG为True时, 该视图函数不会被调用, 因为Django要暴露错误信息以方便开发者调试
def custom_404_interceptor(request, exception): # 该视图函数用于无效页面的重定向
    return redirect('User:login')