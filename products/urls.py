from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('my-products/', views.my_products, name='my_products'),
    path('history/', views.product_history, name='product_history'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('<int:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # Borrow/Lend URLs
    path('<int:product_id>/borrow/', views.borrow_request_create, name='borrow_request_create'),
    path('borrow-requests/<int:request_id>/', views.borrow_request_detail, name='borrow_request_detail'),
    path('borrow-requests/<int:request_id>/approve/', views.borrow_request_approve, name='borrow_request_approve'),
    path('borrow-requests/<int:request_id>/reject/', views.borrow_request_reject, name='borrow_request_reject'),
    path('borrow-requests/<int:request_id>/return/', views.borrow_request_return, name='borrow_request_return'),
    path('borrow-requests/<int:request_id>/cancel/', views.borrow_request_cancel, name='borrow_request_cancel'),
    path('my-borrow-requests/', views.my_borrow_requests, name='my_borrow_requests'),
    path('my-lend-requests/', views.my_lend_requests, name='my_lend_requests'),
    
    # OTP URLs (Uber-style verification)
    path('borrow-requests/<int:request_id>/generate-acceptance-otp/', views.generate_acceptance_otp, name='generate_acceptance_otp'),
    path('borrow-requests/<int:request_id>/verify-acceptance-otp/', views.verify_acceptance_otp, name='verify_acceptance_otp'),
    path('borrow-requests/<int:request_id>/generate-return-otp/', views.generate_return_otp, name='generate_return_otp'),
    path('borrow-requests/<int:request_id>/verify-return-otp/', views.verify_return_otp, name='verify_return_otp'),
    path('borrow-requests/<int:request_id>/resend-otp/<str:otp_type>/', views.resend_otp_view, name='resend_otp'),
    
    # Purchase/Buy URLs
    path('<int:product_id>/purchase/', views.purchase_request_create, name='purchase_request_create'),
    path('purchase-requests/<int:request_id>/', views.purchase_request_detail, name='purchase_request_detail'),
    path('purchase-requests/<int:request_id>/approve/', views.purchase_request_approve, name='purchase_request_approve'),
    path('purchase-requests/<int:request_id>/reject/', views.purchase_request_reject, name='purchase_request_reject'),
    path('purchase-requests/<int:request_id>/cancel/', views.purchase_request_cancel, name='purchase_request_cancel'),
    path('my-purchase-requests/', views.my_purchase_requests, name='my_purchase_requests'),
    path('my-sale-requests/', views.my_sale_requests, name='my_sale_requests'),
    
    # Purchase OTP URLs (Uber-style verification)
    path('purchase-requests/<int:request_id>/verify-handover-otp/', views.verify_purchase_handover_otp, name='verify_purchase_handover_otp'),
    path('purchase-requests/<int:request_id>/resend-purchase-otp/', views.resend_purchase_otp, name='resend_purchase_otp'),
    
    # AJAX endpoints
    path('pending-requests-count/', views.get_pending_requests_count, name='get_pending_requests_count'),
    path('borrow-requests/<int:request_id>/otp-status/', views.get_otp_status, name='get_otp_status'),
    
    # Map and Location URLs
    path('map/', views.product_map, name='product_map'),
    path('<int:product_id>/distance/', views.product_distance_api, name='product_distance_api'),
    path('meeting-point/<int:request_id>/<str:request_type>/', views.meeting_point_api, name='meeting_point_api'),
    path('toggle-location/<int:request_id>/<str:request_type>/', views.toggle_location_sharing, name='toggle_location_sharing'),
]
