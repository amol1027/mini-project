from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete_view, name='user_delete'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('export/transactions/', views.export_transactions_csv, name='export_transactions'),
    path('export/users/', views.export_users_csv, name='export_users'),
    path('export/dashboard/', views.export_dashboard_summary_csv, name='export_dashboard'),
]
