from django.urls import path
from . import views

urlpatterns = [
    path('copilot/', views.copilot, name='copilot'),
    path('delete_all_conversation_history/', views.delete_all_conversation_history, name='delete_all_conversation_history'),

]
