from django.urls import path
from . import views

urlpatterns = [
    path('venue_layout/', views.venue_layout, name='venue_layout'),
    path('layout/', views.layout, name='layout'),
    path('get_floor_data/', views.get_floor_data, name='get_floor_data'),
]
