from django.contrib import admin
from .models import Product, BorrowRequest
from .history_models import ProductHistory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'condition', 'listing_type', 'price', 'seller', 'is_available', 'is_currently_borrowed', 'views', 'created_at']
    list_filter = ['category', 'condition', 'listing_type', 'is_available', 'is_currently_borrowed', 'created_at']
    search_fields = ['title', 'description', 'seller__email', 'seller__name']
    list_editable = ['is_available']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('title', 'description', 'category', 'condition')
        }),
        ('Listing Type & Pricing', {
            'fields': ('listing_type', 'price', 'borrow_price_per_day', 'borrow_deposit', 'max_borrow_days')
        }),
        ('Seller & Availability', {
            'fields': ('seller', 'is_available', 'is_currently_borrowed')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'borrower', 'lender', 'status', 'requested_days', 'total_cost', 'start_date', 'expected_return_date', 'created_at']
    list_filter = ['status', 'created_at', 'start_date', 'expected_return_date']
    search_fields = ['product__title', 'borrower__email', 'borrower__name', 'lender__email', 'lender__name']
    readonly_fields = ['request_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('product', 'borrower', 'lender', 'status')
        }),
        ('Borrowing Terms', {
            'fields': ('requested_days', 'total_cost', 'deposit_amount', 'message')
        }),
        ('Dates', {
            'fields': ('request_date', 'approved_date', 'start_date', 'expected_return_date', 'actual_return_date')
        }),
        ('Lender Response', {
            'fields': ('lender_response',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductHistory)
class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'title', 'user', 'action', 'action_date', 'price', 'views_at_action']
    list_filter = ['action', 'action_date', 'category', 'listing_type']
    search_fields = ['title', 'description', 'user__email', 'user__name']
    readonly_fields = ['product_id', 'title', 'description', 'category', 'condition', 
                      'listing_type', 'price', 'user', 'action', 'action_date', 
                      'reason', 'views_at_action', 'was_available']
    date_hierarchy = 'action_date'
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product_id', 'title', 'description', 'category', 'condition', 'listing_type')
        }),
        ('Action Details', {
            'fields': ('user', 'action', 'action_date', 'reason')
        }),
        ('Product Stats at Action', {
            'fields': ('price', 'views_at_action', 'was_available'),
            'classes': ('collapse',)
        }),
    )

