from django.shortcuts import render, redirect

from Venue.models import Venue


def home(request):
    if request.method == 'GET':
        # 先获取所有的Venue
        venues = Venue.objects.all()
        # 然后把所有的Venue传给模板
        return render(request, 'Venue/home.html', {'venues': venues})
    if request.method == 'POST':
        # 获取用户提交的数据
        name = request.POST.get('name')
        address = request.POST.get('address')
        # 创建一个新的Venue
        Venue.objects.create(name=name, address=address)
        # 重定向到home页面
        return redirect('home')
