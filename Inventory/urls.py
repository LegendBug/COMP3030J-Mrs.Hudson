from django.urls import path
from . import views
from .views import (category_detail_view, edit_inventory_category, delete_inventory_category, edit_item, return_item,
                    delete_item)

urlpatterns = [
    path('inventory/<str:space_type>/<int:space_id>/', views.inventory, name='inventory'),
    #path('inventory/<str:current_access_type>/<int:current_access_id>/', views.inventory, name='inventory'),
    path('create_res_application', views.create_res_application, name='create_res_application'),
    path('category/<int:category_id>/details/', category_detail_view, name='category_detail'),
    path('edit-category/<int:category_id>/', edit_inventory_category, name='edit-category'),
    path('delete-category/<int:category_id>/', delete_inventory_category, name='delete-category'),
    path('item/<int:item_id>/edit/', edit_item, name='edit_item'),
    path('item/<int:item_id>/return/', views.return_item, name='return_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('refresh_data/', views.refresh_data, name='refresh_data'),
]
