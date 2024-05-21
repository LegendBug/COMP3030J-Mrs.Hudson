from django.urls import path

from Booth import views

urlpatterns = [
    path('booth/<int:booth_id>/', views.booth, name='booth'),
    path('refresh_data/', views.refresh_data, name='refresh_data'),
    path('create_booth_application/', views.create_booth_application, name='create_booth_application')
]
