"""
Context processors for products app
Provides global template context variables
"""


def pending_borrow_requests(request):
    """
    Context processor to add pending borrow request count to all templates
    Shows count of pending requests where user is the lender
    """
    if 'user_id' in request.session:
        from registration.models import User
        from .models import BorrowRequest
        
        try:
            user = User.objects.get(id=request.session['user_id'])
            # Count pending requests where this user is the lender
            pending_count = BorrowRequest.objects.filter(
                lender=user,
                status='pending'
            ).count()
            return {'pending_borrow_requests_count': pending_count}
        except User.DoesNotExist:
            pass
    
    return {'pending_borrow_requests_count': 0}
