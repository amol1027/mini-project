from django.contrib import admin
from .models import Product, BorrowRequest

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

