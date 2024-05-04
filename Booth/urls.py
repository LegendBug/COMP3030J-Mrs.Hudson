from django.urls import path

from Booth import views

urlpatterns = [
    path('booth/<int:booth_id>/', views.booth, name='booth'),
]
