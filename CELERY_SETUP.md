# Celery Setup and Configuration Guide

## Overview
This document explains how to set up and use Celery for background task processing in the Student Resource Exchange platform. Celery enables automated overdue detection, reminders, and other periodic tasks.

---

## What is Celery?

**Celery** is a distributed task queue system for Python that allows you to run background tasks asynchronously. It's perfect for:
- Periodic tasks (scheduled jobs)
- Long-running operations
- Automated notifications
- Task scheduling

**Key Components:**
1. **Celery Worker** - Executes tasks in the background
2. **Redis** - Message broker (task queue)
3. **Celery Beat** - Scheduler for periodic tasks
4. **Django-Celery-Beat** - Database-backed scheduler with admin interface

---

## Installation

### 1. Install Python Dependencies

The required packages are already listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- `celery>=5.3.4` - Core Celery library
- `redis>=5.0.0` - Python Redis client
- `django-celery-beat>=2.5.0` - Django integration for periodic tasks

### 2. Install and Start Redis Server

**Redis** is required as the message broker for Celery.

#### Windows:

**Option A: Using Windows Subsystem for Linux (WSL)**
```bash
# Install WSL if not already installed
wsl --install

# In WSL terminal:
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option B: Using Memurai (Redis for Windows)**
1. Download from: https://www.memurai.com/
2. Install and start the service
3. Default runs on `localhost:6379`

**Option C: Using Docker**
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# macOS (using Homebrew)
brew install redis
brew services start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

---

## Project Structure

After setup, your project has these Celery-related files:

```
Student_Resource_Exchange/
├── __init__.py              # Imports Celery app
├── celery.py                # Celery configuration
└── settings.py              # Django settings with Celery config

products/
├── decorators.py            # Custom decorators (@login_required)
├── tasks.py                 # Celery tasks for products app
└── views.py                 # Views using decorators
```

---

## Configuration Files

### 1. `Student_Resource_Exchange/celery.py`
Defines the Celery application and periodic task schedules.

**Key configurations:**
- Task auto-discovery from all apps
- Periodic task schedule (beat schedule)
- Two scheduled tasks:
  - `check_overdue_borrow_requests` - Runs every hour
  - `send_return_reminders` - Runs daily at 9:00 AM

### 2. `Student_Resource_Exchange/settings.py`
Django settings for Celery integration.

**Key settings:**
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

### 3. `products/tasks.py`
Contains all background tasks for the products app.

**Available tasks:**
1. `check_overdue_borrow_requests()` - Marks overdue items
2. `send_return_reminders()` - Sends reminders before due date
3. `send_overdue_notification()` - Notifies lender about overdue
4. `send_return_reminder_notification()` - Notifies borrower about return
5. `cleanup_expired_requests()` - Archives old requests

---

## Database Migration

Before running Celery, apply migrations for django-celery-beat:

```bash
python manage.py migrate
```

This creates tables for:
- Periodic tasks
- Crontab schedules
- Interval schedules
- Solar schedules

---

## Running Celery

You need **three** terminal windows running simultaneously:

### Terminal 1: Django Development Server
```powershell
python manage.py runserver
```

### Terminal 2: Celery Worker
The worker executes background tasks.

```powershell
celery -A Student_Resource_Exchange worker --loglevel=info --pool=solo
```

**Flags explained:**
- `-A Student_Resource_Exchange` - App name
- `worker` - Start worker process
- `--loglevel=info` - Show informational logs
- `--pool=solo` - Windows-compatible execution pool

**On Linux/Mac (use default pool):**
```bash
celery -A Student_Resource_Exchange worker --loglevel=info
```

### Terminal 3: Celery Beat (Scheduler)
The beat scheduler triggers periodic tasks at scheduled times.

```powershell
celery -A Student_Resource_Exchange beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Flags explained:**
- `beat` - Start beat scheduler
- `--scheduler django_celery_beat.schedulers:DatabaseScheduler` - Use database scheduler

---

## Verifying Setup

### 1. Check Worker is Running
In the worker terminal, you should see:
```
[2025-10-21 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-21 10:00:00,000: INFO/MainProcess] celery@hostname ready.
```

### 2. Check Beat is Running
In the beat terminal, you should see:
```
[2025-10-21 10:00:00,000: INFO/MainProcess] beat: Starting...
[2025-10-21 10:00:00,000: INFO/MainProcess] Scheduler: Sending due task check-overdue-borrows-every-hour
```

### 3. Test a Task Manually

Open Django shell:
```bash
python manage.py shell
```

Run a test task:
```python
from products.tasks import check_overdue_borrow_requests

# Execute immediately
result = check_overdue_borrow_requests.delay()

# Check result
print(result.get())
```

---

## Scheduled Tasks

### Current Schedule

| Task | Frequency | Time | Purpose |
|------|-----------|------|---------|
| `check_overdue_borrow_requests` | Every hour | :00 | Mark active borrows as overdue |
| `send_return_reminders` | Daily | 9:00 AM | Remind borrowers 2 days before due |

### Managing Schedules via Admin

1. Navigate to `http://localhost:8000/admin/`
2. Go to **Periodic Tasks** section
3. You can:
   - Add new periodic tasks
   - Modify schedules
   - Enable/disable tasks
   - View task history

**Example: Change reminder time**
1. Click on "Periodic tasks"
2. Find "send-return-reminders-daily"
3. Edit the crontab schedule (e.g., change hour to 8 for 8:00 AM)
4. Save

---

## Task Details

### 1. Check Overdue Borrow Requests

**Task:** `products.tasks.check_overdue_borrow_requests`

**What it does:**
- Finds all `active` borrow requests with `expected_return_date < today`
- Updates status from `active` to `overdue`
- Triggers overdue notifications

**Runs:** Every hour at minute 0

**Manual execution:**
```python
from products.tasks import check_overdue_borrow_requests
check_overdue_borrow_requests.delay()
```

### 2. Send Return Reminders

**Task:** `products.tasks.send_return_reminders`

**What it does:**
- Finds `active` borrows with return date in 2 days
- Sends reminder notifications to borrowers
- Helps prevent overdue returns

**Runs:** Daily at 9:00 AM

**Manual execution:**
```python
from products.tasks import send_return_reminders
send_return_reminders.delay()
```

### 3. Cleanup Expired Requests

**Task:** `products.tasks.cleanup_expired_requests`

**What it does:**
- Finds old cancelled/rejected requests (>90 days)
- Logs them for archival (doesn't delete by default)

**Note:** Currently disabled in schedule. To enable, add to `celery.py`:
```python
'cleanup-expired-requests-weekly': {
    'task': 'products.tasks.cleanup_expired_requests',
    'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2:00 AM
},
```

---

## Custom Decorators

### Login Required Decorator

**File:** `products/decorators.py`

**Usage:**
```python
from products.decorators import login_required

@login_required
def my_view(request):
    # User is guaranteed to be logged in
    user_id = request.session['user_id']
    # ... view logic
```

**Benefits:**
- Eliminates repetitive session checks
- Centralized authentication logic
- Cleaner, more maintainable code
- Consistent error messages

### Available Decorators

| Decorator | Purpose | Usage |
|-----------|---------|-------|
| `@login_required` | User must be logged in | All authenticated views |
| `@owner_required` | User must own the product | Edit/delete product |
| `@lender_required` | User must be the lender | Approve/reject/return |
| `@borrower_required` | User must be the borrower | Cancel request |
| `@request_participant_required` | User must be borrower or lender | View request details |

**Example with multiple decorators:**
```python
@login_required
@owner_required
def edit_product(request, product_id):
    # User is logged in AND owns this product
    pass
```

---

## Monitoring and Debugging

### View Logs

**Worker logs** show task execution:
```
[2025-10-21 10:00:00,000: INFO/MainProcess] Task products.tasks.check_overdue_borrow_requests[...] received
[2025-10-21 10:00:00,100: INFO/MainProcess] Task products.tasks.check_overdue_borrow_requests[...] succeeded
```

**Beat logs** show scheduling:
```
[2025-10-21 10:00:00,000: INFO/MainProcess] Scheduler: Sending due task check-overdue-borrows-every-hour
```

### Common Issues

#### 1. "Connection refused" error
**Problem:** Redis not running
**Solution:** Start Redis server

#### 2. Tasks not executing
**Problem:** Worker or beat not running
**Solution:** Check all 3 terminals are active

#### 3. "ImportError" in tasks
**Problem:** Circular import or missing module
**Solution:** Check import order in tasks.py

#### 4. Windows "pool" error
**Problem:** Default pool doesn't work on Windows
**Solution:** Use `--pool=solo` flag

---

## Production Deployment

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A Student_Resource_Exchange worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.error.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A Student_Resource_Exchange beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.error.log
```

### Using Systemd (Linux)

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A Student_Resource_Exchange worker --detach

[Install]
WantedBy=multi-user.target
```

### Environment Variables

For production, set:
```bash
export DJANGO_SETTINGS_MODULE=Student_Resource_Exchange.settings
export CELERY_BROKER_URL=redis://production-redis:6379/0
```

---

## Testing Tasks

### Unit Testing

Create `products/tests_tasks.py`:

```python
from django.test import TestCase
from products.tasks import check_overdue_borrow_requests
from products.models import BorrowRequest
from datetime import date, timedelta

class CeleryTasksTestCase(TestCase):
    def test_overdue_detection(self):
        # Create test borrow request
        request = BorrowRequest.objects.create(
            status='active',
            expected_return_date=date.today() - timedelta(days=1)
        )
        
        # Run task
        result = check_overdue_borrow_requests()
        
        # Verify
        request.refresh_from_db()
        self.assertEqual(request.status, 'overdue')
```

### Manual Testing

```python
# Django shell
python manage.py shell

# Import and run task
from products.tasks import check_overdue_borrow_requests
result = check_overdue_borrow_requests.delay()

# Check result
print(result.get(timeout=10))
```

---

## Performance Tips

### 1. Task Optimization
- Keep tasks small and focused
- Avoid long-running operations
- Use batch processing for large datasets

### 2. Redis Optimization
- Configure Redis maxmemory policy
- Monitor Redis memory usage
- Use Redis persistence for reliability

### 3. Worker Scaling
```bash
# Run multiple workers
celery -A Student_Resource_Exchange worker --concurrency=4
```

### 4. Rate Limiting
```python
@shared_task(rate_limit='10/m')  # Max 10 calls per minute
def send_notification():
    pass
```

---

## Troubleshooting Checklist

- [ ] Redis is running (`redis-cli ping`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Worker is running (check terminal)
- [ ] Beat is running (check terminal)
- [ ] Django server is running
- [ ] Check logs for errors
- [ ] Verify task imports correctly
- [ ] Check Redis connection in settings

---

## Further Reading

- **Celery Documentation:** https://docs.celeryq.dev/
- **Django-Celery-Beat:** https://django-celery-beat.readthedocs.io/
- **Redis Documentation:** https://redis.io/documentation
- **Best Practices:** https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices

---

## Support

For issues related to:
- **Celery setup:** Check worker/beat logs
- **Task execution:** Check task code in `products/tasks.py`
- **Scheduling:** Check Django admin periodic tasks
- **Redis connection:** Verify Redis server is running

---

**Version:** 1.0  
**Last Updated:** October 21, 2025  
**Maintainer:** Student Resource Exchange Development Team
