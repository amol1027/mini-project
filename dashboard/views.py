from django.shortcuts import render, redirect
from django.contrib import messages
from registration.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

def dashboard_view(request):
    """
    Admin dashboard view - Only accessible to admin users
    """
    # Check if user is logged in and is admin
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('profile:profile')  # Redirect non-admins to profile
    
    # Get current user
    try:
        current_user = User.objects.get(id=request.session['user_id'])
        if not current_user.is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('profile:profile')
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        request.session.flush()
        return redirect('login:login')
    
    # Calculate statistics
    total_users = User.objects.count()
    verified_users = User.objects.filter(email_verified=True).count()
    unverified_users = total_users - verified_users
    
    # Recent users (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_users = User.objects.filter(created_at__gte=seven_days_ago).count()
    
    # Users by rating
    high_rated = User.objects.filter(rating__gte=4).count()
    medium_rated = User.objects.filter(rating__gte=2, rating__lt=4).count()
    low_rated = User.objects.filter(rating__lt=2).count()
    
    # Get latest users
    latest_users = User.objects.order_by('-created_at')[:10]
    
    # Get users with addresses
    users_with_address = User.objects.filter(
        Q(address_line1__isnull=False) & ~Q(address_line1='')
    ).count()
    
    # Calculate percentages
    verified_percentage = (verified_users / total_users * 100) if total_users > 0 else 0
    address_percentage = (users_with_address / total_users * 100) if total_users > 0 else 0
    
    context = {
        'current_user': current_user,
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'recent_users': recent_users,
        'high_rated': high_rated,
        'medium_rated': medium_rated,
        'low_rated': low_rated,
        'latest_users': latest_users,
        'users_with_address': users_with_address,
        'verified_percentage': verified_percentage,
        'address_percentage': address_percentage,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def user_list_view(request):
    """
    Display all users in a table - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('profile:profile')
    
    # Get all users
    users = User.objects.order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(college_id__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
        'total_count': users.count(),
    }
    
    return render(request, 'dashboard/user_list.html', context)

def user_detail_view(request, user_id):
    """
    Display detailed information about a specific user - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('profile:profile')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard:user_list')
    
    context = {
        'user': user,
    }
    
    return render(request, 'dashboard/user_detail.html', context)
