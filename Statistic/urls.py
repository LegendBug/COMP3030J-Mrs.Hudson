from django.urls import path
from . import views

urlpatterns = [
    path('statistic/', views.statistic, name='statistic'),
]
