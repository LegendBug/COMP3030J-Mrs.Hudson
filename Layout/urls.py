from django.urls import path
from . import views

urlpatterns = [
    path('venue_layout/', views.venue_layout, name='venue_layout'),
    path('layout/', views.layout, name='layout'),
    path('synchronize_data/', views.synchronize_data, name='synchronize_data'),
    path('create_sublayer/', views.create_sublayer, name='create_sublayer'),
]
