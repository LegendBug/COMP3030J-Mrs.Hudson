from django.urls import path
from . import views

urlpatterns = [
    path('venue_layout/', views.venue_layout, name='venue_layout'),
    path('layout/', views.layout, name='layout')
]
