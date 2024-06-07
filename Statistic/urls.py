from django.urls import path
from . import views

urlpatterns = [
    path('statistic/', views.statistic, name='statistic'),
    path('get_consumption_data/<int:year>/', views.get_consumption_data, name='get_consumption_data'),
    path('get_venues/', views.get_venues, name='get_venues'),
    path('get_consumption_data_by_venue/<str:venue_name>/<int:year>/', views.get_consumption_data_by_venue, name='get_consumption_data_by_venue'),

    path('monitor_venue/', views.monitor_venue, name='monitor_venue'),
    path('monitor/query_flow_by_day/', views.query_flow_by_day, name='query_flow_by_day'),
    path('recognize_flow/', views.recognize_flow, name='recognize_flow'),
    path('monitor/capture/<int:monitor_id>/', views.capture, name='capture'),
    path('refresh_data/', views.refresh_data, name='refresh_data'),
    path('synchronize_monitors_data/', views.synchronize_monitors_data, name='synchronize_monitors_data'),
    path('add_monitor/', views.add_monitor, name='add_monitor'),
    path('edit_monitor/', views.edit_monitor, name='edit_monitor'),
    path('delete_monitor/', views.delete_monitor, name='delete_monitor'),

    path('add_simulated_data/', views.add_simulated_data, name='add_simulated_data'),
]

