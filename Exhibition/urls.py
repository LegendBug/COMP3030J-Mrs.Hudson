from django.urls import path

from Exhibition import views

urlpatterns = [
    path('exhibition/<int:exhibition_id>/', views.exhibition, name='exhibition'),
    path('create_exhibit_application/', views.create_exhibit_application, name='create_exhibit_application'),
]
