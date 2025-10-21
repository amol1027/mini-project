"""
Celery configuration for Student Resource Exchange
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Student_Resource_Exchange.settings')

# Create Celery app
app = Celery('Student_Resource_Exchange')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery configuration"""
    print(f'Request: {self.request!r}')


# Configure periodic tasks
app.conf.beat_schedule = {
    'check-overdue-borrows-every-hour': {
        'task': 'products.tasks.check_overdue_borrow_requests',
        'schedule': crontab(minute=0),  # Run every hour at minute 0
    },
    'send-return-reminders-daily': {
        'task': 'products.tasks.send_return_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9:00 AM
    },
}
