"""
Celery tasks for products app
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='products.tasks.check_overdue_borrow_requests')
def check_overdue_borrow_requests():
    """
    Periodic task to check for overdue borrow requests and update their status.
    Runs every hour to mark active borrows as overdue if past expected return date.
    
    Returns:
        dict: Statistics about processed requests
    """
    from products.models import BorrowRequest
    
    today = date.today()
    
    # Find all active borrow requests that are past their expected return date
    overdue_requests = BorrowRequest.objects.filter(
        status='active',
        expected_return_date__lt=today
    )
    
    count = overdue_requests.count()
    
    if count > 0:
        # Cache IDs before bulk update (queryset gets mutated)
        overdue_ids = list(overdue_requests.values_list('id', flat=True))
        
        # Update status to overdue
        updated = overdue_requests.update(status='overdue')
        
        logger.info(f'Marked {updated} borrow requests as overdue')
        
        # Send notifications to lenders about overdue items using cached IDs
        if overdue_ids:
            for request_id in overdue_ids:
                send_overdue_notification.delay(request_id)
            logger.info(f'Queued {len(overdue_ids)} overdue notifications')
        
        return {
            'status': 'success',
            'marked_overdue': updated,
            'notifications_queued': len(overdue_ids),
            'timestamp': str(timezone.now())
        }
    else:
        logger.info('No overdue borrow requests found')
        return {
            'status': 'success',
            'marked_overdue': 0,
            'timestamp': str(timezone.now())
        }


@shared_task(name='products.tasks.send_return_reminders')
def send_return_reminders():
    """
    Periodic task to send reminders to borrowers about upcoming return dates.
    Sends reminders 2 days before expected return date.
    Runs daily at 9:00 AM.
    
    Returns:
        dict: Statistics about sent reminders
    """
    from products.models import BorrowRequest
    
    # Calculate date 2 days from now
    reminder_date = date.today() + timedelta(days=2)
    
    # Find active borrows with return date in 2 days
    upcoming_returns = BorrowRequest.objects.filter(
        status='active',
        expected_return_date=reminder_date
    )
    
    count = upcoming_returns.count()
    
    if count > 0:
        # Cache IDs for efficient iteration
        reminder_ids = list(upcoming_returns.values_list('id', flat=True))
        
        logger.info(f'Sending return reminders for {count} requests')
        
        # Queue notification tasks using cached IDs
        if reminder_ids:
            for request_id in reminder_ids:
                send_return_reminder_notification.delay(request_id)
        
        return {
            'status': 'success',
            'reminders_sent': len(reminder_ids),
            'timestamp': str(timezone.now())
        }
    else:
        logger.info('No upcoming returns requiring reminders')
        return {
            'status': 'success',
            'reminders_sent': 0,
            'timestamp': str(timezone.now())
        }


@shared_task(name='products.tasks.send_overdue_notification')
def send_overdue_notification(request_id):
    """
    Send notification to lender about overdue item.
    This is a placeholder - integrate with your notification system.
    
    Args:
        request_id: ID of the overdue borrow request
    """
    from products.models import BorrowRequest
    
    try:
        borrow_request = BorrowRequest.objects.get(id=request_id)
        
        # Calculate days overdue
        days_overdue = (date.today() - borrow_request.expected_return_date).days
        
        # Log the notification (replace with actual notification system)
        logger.warning(
            f'OVERDUE: {borrow_request.borrower.name} has not returned '
            f'"{borrow_request.product.title}" to {borrow_request.lender.name}. '
            f'Days overdue: {days_overdue}'
        )
        
        # TODO: Integrate with email/SMS notification system
        # Example:
        # send_email(
        #     to=borrow_request.lender.email,
        #     subject=f'Item Overdue: {borrow_request.product.title}',
        #     message=f'Your item has not been returned. It is {days_overdue} days overdue.'
        # )
        
        # TODO: Create in-app notification via chat system
        # from chat.models import Message
        # Message.objects.create(
        #     conversation=get_or_create_conversation(borrow_request.lender, borrow_request.borrower),
        #     sender=None,  # System message
        #     content=f'Reminder: The borrowed item "{borrow_request.product.title}" is {days_overdue} days overdue.'
        # )
        
        return {
            'status': 'success',
            'request_id': request_id,
            'days_overdue': days_overdue
        }
        
    except BorrowRequest.DoesNotExist:
        logger.error(f'BorrowRequest {request_id} not found')
        return {'status': 'error', 'message': 'Request not found'}


@shared_task(name='products.tasks.send_return_reminder_notification')
def send_return_reminder_notification(request_id):
    """
    Send reminder notification to borrower about upcoming return date.
    This is a placeholder - integrate with your notification system.
    
    Args:
        request_id: ID of the borrow request
    """
    from products.models import BorrowRequest
    
    try:
        borrow_request = BorrowRequest.objects.get(id=request_id)
        
        # Calculate days until return
        days_until_return = (borrow_request.expected_return_date - date.today()).days
        
        # Log the reminder (replace with actual notification system)
        logger.info(
            f'REMINDER: {borrow_request.borrower.name} needs to return '
            f'"{borrow_request.product.title}" to {borrow_request.lender.name} '
            f'in {days_until_return} days (by {borrow_request.expected_return_date})'
        )
        
        # TODO: Integrate with email/SMS notification system
        # Example:
        # send_email(
        #     to=borrow_request.borrower.email,
        #     subject=f'Return Reminder: {borrow_request.product.title}',
        #     message=f'Please remember to return the borrowed item in {days_until_return} days.'
        # )
        
        # TODO: Create in-app notification
        
        return {
            'status': 'success',
            'request_id': request_id,
            'days_until_return': days_until_return
        }
        
    except BorrowRequest.DoesNotExist:
        logger.error(f'BorrowRequest {request_id} not found')
        return {'status': 'error', 'message': 'Request not found'}


@shared_task(name='products.tasks.cleanup_expired_requests')
def cleanup_expired_requests():
    """
    Optional task to clean up old cancelled/rejected requests.
    Runs weekly to archive or delete very old requests (> 90 days).
    
    Returns:
        dict: Statistics about cleaned requests
    """
    from products.models import BorrowRequest
    
    cutoff_date = timezone.now() - timedelta(days=90)
    
    # Find old cancelled/rejected requests
    old_requests = BorrowRequest.objects.filter(
        Q(status='cancelled') | Q(status='rejected'),
        updated_at__lt=cutoff_date
    )
    
    count = old_requests.count()
    
    if count > 0:
        # Option 1: Delete (be careful with this!)
        # old_requests.delete()
        
        # Option 2: Just log (safer approach)
        logger.info(f'Found {count} old requests that could be archived')
        
        return {
            'status': 'success',
            'old_requests_found': count,
            'timestamp': str(timezone.now())
        }
    else:
        logger.info('No old requests to clean up')
        return {
            'status': 'success',
            'old_requests_found': 0,
            'timestamp': str(timezone.now())
        }
