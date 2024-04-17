from django.urls import path
from . import views
from .views import category_detail_view, edit_inventory_category, delete_inventory_category

urlpatterns = [
    path('inventory/', views.inventory, name='inventory'),
    path('category/<int:category_id>/details/', category_detail_view, name='category_detail'),
    path('edit-category/<int:category_id>/', edit_inventory_category, name='edit-category'),
    path('delete-category/<int:category_id>/', delete_inventory_category, name='delete-category'),
]
