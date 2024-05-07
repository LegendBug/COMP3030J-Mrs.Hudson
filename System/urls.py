from django.urls import path
from . import views

urlpatterns = [
    path('copilot/', views.copilot, name='copilot')
]
