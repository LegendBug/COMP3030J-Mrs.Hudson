from django.urls import path
from . import views

urlpatterns = [
    path('statistic/', views.statistic, name='statistic'),
    path('get_consumption_data/<int:year>/', views.get_consumption_data, name='get_consumption_data'),
    path('get_venues/', views.get_venues, name='get_venues'),
    path('get_consumption_data_by_venue/<str:venue_name>/<int:year>/', views.get_consumption_data_by_venue, name='get_consumption_data_by_venue'),

    path('recognize_flow/', views.recognize_flow, name='recognize_flow'),
]

