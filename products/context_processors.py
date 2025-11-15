"""
Context processors for products app
Provides global template context variables
"""
from django.core.cache import cache
from .models import BorrowRequest


def pending_borrow_requests(request):
    """
    Context processor to add pending borrow request count to all templates
    Shows count of pending requests where user is the lender
    Uses Django's cache framework to reduce database queries
    """
    # Check if user is authenticated using session
    user_id = request.session.get('user_id')
    
    if not user_id:
        return {'pending_borrow_requests_count': 0}
    
    # Generate cache key for this user's pending requests count
    cache_key = f'pending_borrow_requests_count_{user_id}'
    
    # Try to get the count from cache first
    pending_count = cache.get(cache_key)
    
    if pending_count is None:
        # Cache miss - query the database
        pending_count = BorrowRequest.objects.filter(
            lender_id=user_id,
            status='pending'
        ).count()
        
        # Store in cache for 5 minutes (300 seconds)
        # This cache is invalidated when borrow request status changes
        cache.set(cache_key, pending_count, 300)
    
    return {'pending_borrow_requests_count': pending_count}
