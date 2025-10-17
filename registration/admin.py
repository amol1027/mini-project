from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'college_id', 'name', 'rating', 'email_verified', 'created_at']
    list_filter = ['email_verified', 'created_at', 'country']
    search_fields = ['email', 'college_id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('email', 'password_hash', 'college_id', 'name', 'email_verified', 'rating')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state_province', 'zip_postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
