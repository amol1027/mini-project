from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('', views.register, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]
