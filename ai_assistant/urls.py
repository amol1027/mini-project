from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/get-history/', views.get_chat_history, name='get_history'),
    path('api/clear-history/', views.clear_chat_history, name='clear_history'),
    path('api/suggestions/', views.get_suggestions, name='get_suggestions'),
]
