from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('message/', views.view_message, name='view_message'),
    path('message/detail/<int:message_id>/', views.view_message_detail, name='view_message_detail'),
    path('message/reply_message/<int:message_id>/', views.reply_message, name='reply_message'),
    path('application/detail/<str:application_type>/<int:application_id>/',
         views.view_application_detail, name='view_application_detail'),
    path('application/reject_application/<str:application_type>/<int:application_id>/',
         views.reject_application, name='reject_application'),
    path('application/accept_application/<str:application_type>/<int:application_id>/',
         views.accept_application, name='accept_application'),
]
