from django.urls import path
from . import views

urlpatterns = [
    path('venue_layout/', views.venue_layout, name='venue_layout'),
    path('layout/', views.layout, name='layout'),
    path('synchronize_data/', views.synchronize_data, name='synchronize_data'),
    path('add_sublayer/', views.add_sublayer, name='add_sublayer'),
    path('delete_layer/', views.delete_layer, name='delete_layer'),
    path('edit_layer/', views.edit_layer, name='edit_layer'),
    path('add_element/', views.add_element, name='add_element'),
    path('delete_element/', views.delete_element, name='delete_element'),
    path('synchronize_elements_data/', views.synchronize_elements_data, name='synchronize_elements_data'),

]
