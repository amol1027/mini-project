# Quick Start: Celery & Decorators

## Install Dependencies
```powershell
pip install celery redis django-celery-beat
```

## Start Redis (Choose one)
```powershell
# WSL
wsl -e sudo service redis-server start

# Or Docker
docker run -d -p 6379:6379 redis:latest
```

## Apply Migrations
```powershell
python manage.py migrate
```

## Run Services (3 Terminals)

**Terminal 1 - Django:**
```powershell
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```powershell
celery -A Student_Resource_Exchange worker --loglevel=info --pool=solo
```

**Terminal 3 - Celery Beat:**
```powershell
celery -A Student_Resource_Exchange beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## New Decorators Usage

```python
from products.decorators import login_required, owner_required

@login_required
def my_view(request):
    # User is authenticated
    pass

@login_required
@owner_required
def edit_product(request, product_id):
    # User is authenticated AND owns the product
    pass
```

## Available Decorators
- `@login_required` - User must be logged in
- `@owner_required` - User must own the product
- `@lender_required` - User must be the lender
- `@borrower_required` - User must be the borrower
- `@request_participant_required` - User must be involved in request

## Automated Tasks
- **Overdue Detection:** Runs every hour
- **Return Reminders:** Runs daily at 9:00 AM

## Verify Setup
```python
# In Django shell
from products.tasks import check_overdue_borrow_requests
result = check_overdue_borrow_requests.delay()
print(result.get())
```

## Manage Tasks
- Admin: http://localhost:8000/admin/django_celery_beat/
- View and edit periodic tasks
- Check task execution history

---
Full documentation: See `CELERY_SETUP.md`
