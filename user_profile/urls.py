from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('verify-address/', views.verify_address_api, name='verify_address'),
    path('reverse-geocode/', views.reverse_geocode_api, name='reverse_geocode'),
]
