"""
Custom decorators for products app
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required(view_func):
    """
    Decorator to check if user is logged in via session.
    Redirects to login page if not authenticated.
    
    Usage:
        @login_required
        def my_view(request):
            # view logic here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Please login to access this page.')
            return redirect('login:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_required(view_func):
    """
    Decorator to check if user is the owner of the product.
    Must be used after @login_required.
    Expects product_id in view kwargs.
    
    Usage:
        @login_required
        @owner_required
        def edit_product(request, product_id):
            # view logic here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Product
        from django.shortcuts import get_object_or_404
        
        # Get user_id safely from session
        user_id = request.session.get('user_id')
        if user_id is None:
            messages.error(request, 'Please login to access this page.')
            return redirect('login:login')
        
        product_id = kwargs.get('product_id')
        if not product_id:
            messages.error(request, 'Invalid product.')
            return redirect('products:product_list')
        
        product = get_object_or_404(Product, id=product_id)
        
        if product.seller.id != user_id:
            messages.error(request, 'You can only access your own products.')
            return redirect('products:product_detail', product_id=product_id)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def lender_required(view_func):
    """
    Decorator to check if user is the lender of the borrow request.
    Must be used after @login_required.
    Expects request_id in view kwargs.
    
    Usage:
        @login_required
        @lender_required
        def approve_request(request, request_id):
            # view logic here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import BorrowRequest
        from django.shortcuts import get_object_or_404
        
        # Get user_id safely from session
        user_id = request.session.get('user_id')
        if user_id is None:
            messages.error(request, 'Please login to access this page.')
            return redirect('login:login')
        
        request_id = kwargs.get('request_id')
        if not request_id:
            messages.error(request, 'Invalid request.')
            return redirect('products:product_list')
        
        borrow_request = get_object_or_404(BorrowRequest, id=request_id)
        
        if borrow_request.lender.id != user_id:
            messages.error(request, 'Only the lender can perform this action.')
            return redirect('products:borrow_request_detail', request_id=request_id)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def borrower_required(view_func):
    """
    Decorator to check if user is the borrower of the borrow request.
    Must be used after @login_required.
    Expects request_id in view kwargs.
    
    Usage:
        @login_required
        @borrower_required
        def cancel_request(request, request_id):
            # view logic here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import BorrowRequest
        from django.shortcuts import get_object_or_404
        
        # Get user_id safely from session
        user_id = request.session.get('user_id')
        if user_id is None:
            messages.error(request, 'Please login to access this page.')
            return redirect('login:login')
        
        request_id = kwargs.get('request_id')
        if not request_id:
            messages.error(request, 'Invalid request.')
            return redirect('products:product_list')
        
        borrow_request = get_object_or_404(BorrowRequest, id=request_id)
        
        if borrow_request.borrower.id != user_id:
            messages.error(request, 'Only the borrower can perform this action.')
            return redirect('products:borrow_request_detail', request_id=request_id)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def request_participant_required(view_func):
    """
    Decorator to check if user is either borrower or lender of the borrow request.
    Must be used after @login_required.
    Expects request_id in view kwargs.
    
    Usage:
        @login_required
        @request_participant_required
        def view_request_details(request, request_id):
            # view logic here
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import BorrowRequest
        from django.shortcuts import get_object_or_404
        
        # Get user_id safely from session
        user_id = request.session.get('user_id')
        if user_id is None:
            messages.error(request, 'Please login to access this page.')
            return redirect('login:login')
        
        request_id = kwargs.get('request_id')
        if not request_id:
            messages.error(request, 'Invalid request.')
            return redirect('products:product_list')
        
        borrow_request = get_object_or_404(BorrowRequest, id=request_id)
        
        if borrow_request.borrower.id != user_id and borrow_request.lender.id != user_id:
            messages.error(request, 'You do not have permission to view this request.')
            return redirect('products:product_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def rate_limit(max_requests=10, window_seconds=60):
    """
    Simple rate limiting decorator using Django cache.
    Limits requests per user per time window.
    
    Usage:
        @login_required
        @rate_limit(max_requests=10, window_seconds=60)
        def my_api_view(request):
            # view logic here
    
    Args:
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from django.core.cache import cache
            from django.http import JsonResponse
            
            # Get user ID from session
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Create cache key for this user and endpoint
            cache_key = f"rate_limit:{view_func.__name__}:user_{user_id}"
            
            # Get current request count
            request_count = cache.get(cache_key, 0)
            
            if request_count >= max_requests:
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': window_seconds
                }, status=429)
            
            # Increment request count
            cache.set(cache_key, request_count + 1, window_seconds)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
