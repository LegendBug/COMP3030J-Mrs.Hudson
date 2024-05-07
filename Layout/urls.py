from django.urls import path
from . import views

urlpatterns = [
    path('venue_layout/', views.venue_layout, name='venue_layout'),
    path('layout/', views.layout, name='layout'),
    path('synchronize_data/', views.synchronize_data, name='synchronize_data'),
    path('add_sublayer/', views.add_sublayer, name='add_sublayer'),
    path('delete_layer/', views.delete_layer, name='delete_layer'),
    path('edit_layer/', views.edit_layer, name='edit_layer'),

    path('add_fake_konva_element/', views.add_fake_konva_element, name='add_fake_konva_element'),
]
