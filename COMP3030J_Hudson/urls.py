"""
URL configuration for COMP3030J_Hudson project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse
from django.views.generic import RedirectView

from Inventory.views import *
from Layout.views import *
from Statistic.views import *
from System.views import *
from User.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# 当settings.py的DEBUG为True时, handler404不会生效, 因为Django要暴露错误信息以方便开发者调试
handler404 = 'System.views.custom_404_interceptor'  # 该行代码用于无效页面的重定向

urlpatterns = [path('', RedirectView.as_view(pattern_name='User:login', permanent=False)),
               path('admin/', admin.site.urls),
               path('Inventory/', include(('Inventory.urls', 'Inventory'), namespace='Inventory')),
               path('Layout/', include(('Layout.urls', 'Layout'), namespace='Layout')),
               path('Statistic/', include(('Statistic.urls', 'Statistic'), namespace='Statistic')),
               path('System/', include(('System.urls', 'System'), namespace='System')),
               path('User/', include(('User.urls', 'User'), namespace='User')),
               path('Venue/', include(('Venue.urls', 'Venue'), namespace='Venue')),
               path('Exhibition/', include(('Exhibition.urls', 'Exhibition'), namespace='Exhibition')),
               path('Booth/', include(('Booth.urls', 'Booth'), namespace='Booth'))
               ] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
