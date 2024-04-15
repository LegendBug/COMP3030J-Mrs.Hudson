from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('venue/<int:venue_id>', views.venue, name='venue'),
]
