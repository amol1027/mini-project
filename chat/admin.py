from django.contrib import admin
from .models import Conversation, Message, NotificationPreference


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'product', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['buyer__email', 'seller__email', 'product__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['buyer', 'seller', 'product']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__email']
    readonly_fields = ['created_at']
    raw_id_fields = ['conversation', 'sender']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'enable_sound', 'enable_desktop', 'enable_email', 'updated_at']
    list_filter = ['enable_sound', 'enable_desktop', 'enable_email']
    search_fields = ['user__email', 'user__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
