from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('modify_venue/<int:venue_id>', views.modify_venue, name='modify_venue'),
    path('delete_venue/<int:venue_id>', views.delete_venue, name='delete_venue'),
    path('venue/<int:venue_id>', views.venue, name='venue'),
    path('refresh_data/', views.refresh_data, name='refresh_data'),
]
