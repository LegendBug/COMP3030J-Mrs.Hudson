from django.urls import path

from Booth import views

urlpatterns = [
    path('booth/<int:booth_id>/', views.booth, name='booth'),
    path('create_booth_application/', views.create_booth_application, name='create_booth_application')
]
