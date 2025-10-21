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
    
    # AJAX endpoints
    path('pending-requests-count/', views.get_pending_requests_count, name='get_pending_requests_count'),
]
