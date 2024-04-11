from django.shortcuts import render


# 创建展览申请
def create_exhibition_application(request):
    return render(request, 'Exhibition/create_exhibition_application.html')
