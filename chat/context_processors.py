import logging
from django.core.cache import cache
from django.db import DatabaseError
from .models import Conversation

logger = logging.getLogger(__name__)


def unread_messages(request):
    """
    Context processor to add unread message count to all templates
    Uses Django's cache framework to reduce database queries
    """
    user_id = request.session.get('user_id')
    
    if not user_id:
        return {'unread_message_count': 0}
    
    # Generate cache key for this user's unread message count
    cache_key = f'unread_message_count_{user_id}'
    
    # Try to get the count from cache first
    unread_count = cache.get(cache_key)
    
    if unread_count is None:
        # Cache miss - query the database
        from registration.models import User
        try:
            user = User.objects.get(id=user_id)
            unread_count = Conversation.get_total_unread_count(user)
            
            # Store in cache for 30 seconds (for faster updates)
            cache.set(cache_key, unread_count, 30)
        except User.DoesNotExist:
            # User not found - set to 0 and cache it to avoid repeated lookups
            unread_count = 0
            cache.set(cache_key, unread_count, 30)
        except DatabaseError as e:
            # Database connection/timeout error - fail gracefully
            logger.error(f"Database error in unread_messages context processor for user_id {user_id}: {e}")
            unread_count = 0
            # Don't cache the error state to allow retry on next request
    
    return {'unread_message_count': unread_count}
