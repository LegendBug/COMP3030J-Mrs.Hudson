from django.urls import path

from Exhibition import views

urlpatterns = [
    path('create_exhib_application/', views.create_exhib_application, name='create_exhib_application'),
]
