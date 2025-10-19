from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'condition', 'price', 'seller', 'is_available', 'views', 'created_at']
    list_filter = ['category', 'condition', 'is_available', 'created_at']
    search_fields = ['title', 'description', 'seller__email', 'seller__name']
    list_editable = ['is_available']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('title', 'description', 'category', 'condition', 'price')
        }),
        ('Seller & Availability', {
            'fields': ('seller', 'is_available')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

