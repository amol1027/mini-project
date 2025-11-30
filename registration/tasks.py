from celery import shared_task
from registration.models import User
from registration.geocoding_utils import geocode_user
import logging
import time

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def geocode_user_task(self, user_id):
    """
    Async task to geocode user address with rate limiting
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Simple rate limiting - sleep to ensure we don't hit Nominatim too hard
        # even if multiple workers pick up tasks
        time.sleep(1.1) 
        
        success = geocode_user(user)
        
        if not success:
            logger.warning(f"Geocoding failed for user {user_id}")
            return False
            
        return True
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for geocoding task")
        return False
    except Exception as e:
        logger.error(f"Error in geocode_user_task for user {user_id}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
