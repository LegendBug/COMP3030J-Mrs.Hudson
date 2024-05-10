from django.urls import path
from . import views

urlpatterns = [
    path('statistic/', views.statistic, name='statistic'),
    path('get_consumption_data/<int:year>/', views.get_consumption_data, name='get_consumption_data'),
]

