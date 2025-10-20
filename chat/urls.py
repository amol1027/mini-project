from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('conversation/<int:conversation_id>/', views.chat_detail, name='chat_detail'),
    path('start/<int:product_id>/', views.start_conversation, name='start_conversation'),
    path('start/<int:product_id>/with/<int:other_user_id>/', views.start_conversation_with_user, name='start_conversation_with_user'),
    path('send/<int:conversation_id>/', views.send_message, name='send_message'),
    path('get-messages/<int:conversation_id>/', views.get_new_messages, name='get_new_messages'),
    path('unread-count/', views.get_unread_count, name='get_unread_count'),
    path('notification-settings/', views.notification_settings, name='notification_settings'),
    path('notification-preferences/', views.get_notification_preferences, name='get_notification_preferences'),
]
