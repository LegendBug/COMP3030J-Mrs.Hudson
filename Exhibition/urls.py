from django.urls import path

from Exhibition import views

urlpatterns = [
    path('create_exhibit_application/', views.create_exhibit_application, name='create_exhibit_application'),
]
