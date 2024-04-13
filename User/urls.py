from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('message/', views.view_message, name='view_message'),
    path('profile/', views.profile, name='profile'),
    path('message/detail/<int:message_id>/', views.view_message_detail, name='view_message_detail'),
]
