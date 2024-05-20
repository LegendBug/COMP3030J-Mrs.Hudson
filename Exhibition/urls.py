from django.urls import path

from Exhibition import views

urlpatterns = [
    path('exhibition/<int:exhibition_id>/', views.exhibition, name='exhibition'),
    path('refresh_data/', views.refresh_data, name='refresh_data'),
    path('create_exhibit_application/', views.create_exhibit_application, name='create_exhibit_application'),
]
