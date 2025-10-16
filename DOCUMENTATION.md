# 📖 Student Resource Exchange - Technical Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Backend Services](#backend-services)
7. [Authentication & Authorization](#authentication--authorization)
8. [File Structure](#file-structure)
9. [Configuration](#configuration)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)
12. [Development Workflow](#development-workflow)

---

## 1. Introduction

### Project Overview

Student Resource Exchange (SRE) is a Django-based web platform designed to facilitate the sharing and exchange of educational resources among students. The platform provides a secure, user-friendly interface for posting, browsing, borrowing, and lending academic materials.

### Technology Decisions

- **Django**: Chosen for rapid development, built-in admin panel, and robust ORM
- **SQLite**: Default database for development; easily upgradable to PostgreSQL
- **Tailwind CSS**: Utility-first approach for rapid UI development
- **Alpine.js**: Minimal JavaScript for interactive components

### System Requirements

- **Development**:
  - Python 3.8+
  - Node.js 14+
  - 4GB RAM minimum
  - 1GB free disk space

- **Production**:
  - Python 3.8+
  - PostgreSQL 12+ (recommended)
  - Nginx or Apache
  - 2GB RAM minimum
  - SSL certificate

---

## 2. Architecture Overview

### High-Level Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│      Nginx (Reverse Proxy)      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│      Django Application         │
│  ┌──────────────────────────┐   │
│  │     URL Router           │   │
│  └──────────┬───────────────┘   │
│             │                    │
│  ┌──────────▼───────────────┐   │
│  │     Views Layer          │   │
│  └──────────┬───────────────┘   │
│             │                    │
│  ┌──────────▼───────────────┐   │
│  │     Models Layer         │   │
│  └──────────┬───────────────┘   │
└─────────────┼───────────────────┘
              │
              ▼
     ┌────────────────┐
     │   Database     │
     │   (SQLite/     │
     │   PostgreSQL)  │
     └────────────────┘
```

### Application Flow

1. **Request Reception**: User makes HTTP request
2. **URL Routing**: Django URL dispatcher matches pattern
3. **View Processing**: View function/class processes request
4. **Template Rendering**: HTML template rendered with context
5. **Response**: HTTP response sent back to user

### MVC Pattern Implementation

- **Model**: Database models in `models.py`
- **View**: Business logic in `views.py`
- **Template**: HTML templates in `templates/`
- **Controller**: URL configuration in `urls.py`

---

## 3. Database Schema

### Current Models

#### User Model (Django's built-in)
```python
User
├── id (Primary Key)
├── username
├── email
├── password (hashed)
├── first_name
├── last_name
├── date_joined
└── last_login
```

### Planned Models

#### Resource Model
```python
Resource
├── id (Primary Key)
├── owner (Foreign Key → User)
├── title
├── description
├── category
├── condition
├── availability_status
├── images (Many-to-Many → ResourceImage)
├── created_at
└── updated_at
```

#### Transaction Model
```python
Transaction
├── id (Primary Key)
├── resource (Foreign Key → Resource)
├── borrower (Foreign Key → User)
├── lender (Foreign Key → User)
├── borrow_date
├── return_date
├── actual_return_date
├── status
└── created_at
```

#### Review Model
```python
Review
├── id (Primary Key)
├── transaction (Foreign Key → Transaction)
├── reviewer (Foreign Key → User)
├── reviewee (Foreign Key → User)
├── rating (1-5)
├── comment
└── created_at
```

### Database Relationships

```
User ──┐
       │ 1:N
       ├──────> Resource
       │ 1:N
       ├──────> Transaction (as borrower)
       │ 1:N
       ├──────> Transaction (as lender)
       │ 1:N
       └──────> Review (as reviewer/reviewee)

Resource ──> Transaction (1:N)
Transaction ──> Review (1:1 or 1:2)
```

---

## 4. API Endpoints

### Current Endpoints

#### Landing Page
- **GET** `/` - Display landing page
  - Template: `landing/landing.html`
  - Context: None
  - Authentication: Not required

### Planned API Endpoints

#### Authentication
- **POST** `/api/auth/register/` - Register new user
- **POST** `/api/auth/login/` - User login
- **POST** `/api/auth/logout/` - User logout
- **POST** `/api/auth/password-reset/` - Password reset

#### Resources
- **GET** `/api/resources/` - List all resources
- **POST** `/api/resources/` - Create new resource
- **GET** `/api/resources/<id>/` - Get resource details
- **PUT** `/api/resources/<id>/` - Update resource
- **DELETE** `/api/resources/<id>/` - Delete resource

#### Transactions
- **GET** `/api/transactions/` - List user transactions
- **POST** `/api/transactions/` - Create borrow request
- **PUT** `/api/transactions/<id>/` - Update transaction status
- **GET** `/api/transactions/<id>/` - Get transaction details

#### Reviews
- **GET** `/api/reviews/user/<id>/` - Get user reviews
- **POST** `/api/reviews/` - Submit review
- **GET** `/api/reviews/<id>/` - Get review details

---

## 5. Frontend Components

### Page Structure

#### Base Template (`base.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <!-- Meta tags, title, CSS -->
    - Tailwind CSS
    - Alpine.js
    - Inter Font
    - Custom animations
</head>
<body>
    {% block content %}
    {% endblock %}
</body>
</html>
```

#### Landing Page Components

1. **Header/Navigation**
   - Logo with gradient text
   - Desktop navigation menu
   - Mobile hamburger menu
   - Login button

2. **Hero Section**
   - Main heading
   - Subheading with description
   - CTA buttons (Get Started, Learn More)
   - Decorative gradient background

3. **Features Section**
   - 6 feature cards in responsive grid
   - Icons with descriptions
   - Hover animations
   - 3-column layout on desktop

4. **About Section**
   - Mission statement
   - Platform description
   - Center-aligned content

5. **CTA Section**
   - Call-to-action heading
   - Sign-up button
   - Gradient background
   - Center-aligned layout

6. **Footer**
   - Navigation links
   - Social media icons
   - Copyright information

### Styling System

#### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('daisyui'),
  ],
}
```

#### Custom Animations

```css
/* Fade-in animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Card hover effect */
.feature-card {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px
- **Large Desktop**: > 1280px

---

## 6. Backend Services

### Django Apps

#### Landing App
```python
# views.py
from django.shortcuts import render

def landing_page(request):
    """Display the main landing page"""
    return render(request, 'landing/landing.html')
```

#### Theme App
- Manages Tailwind CSS integration
- Provides base templates
- Handles static file compilation

### Middleware Stack

1. **SecurityMiddleware** - Security headers
2. **SessionMiddleware** - Session management
3. **CommonMiddleware** - Common processing
4. **CsrfViewMiddleware** - CSRF protection
5. **AuthenticationMiddleware** - User authentication
6. **MessageMiddleware** - Message framework
7. **XFrameOptionsMiddleware** - Clickjacking protection

### Static Files Management

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'theme/static'),
]

# Tailwind configuration
TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = 'npm'
```

---

## 7. Authentication & Authorization

### Current Implementation

- Using Django's built-in authentication system
- No authentication required for landing page

### Planned Implementation

#### User Registration Flow

1. User submits registration form
2. Validate email uniqueness
3. Hash password using PBKDF2
4. Create user account
5. Send verification email
6. Redirect to login page

#### Login Flow

1. User submits credentials
2. Authenticate against database
3. Create session
4. Set session cookie
5. Redirect to dashboard

#### Permission Levels

- **Anonymous**: View public resources only
- **Student**: Full access to platform features
- **Moderator**: Can moderate content and reviews
- **Admin**: Full system access

---

## 8. File Structure

```
mini project/
│
├── Student_Resource_Exchange/       # Main project directory
│   ├── __init__.py
│   ├── asgi.py                     # ASGI configuration
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # Root URL configuration
│   └── wsgi.py                     # WSGI configuration
│
├── landing/                         # Landing page app
│   ├── migrations/                 # Database migrations
│   ├── templates/
│   │   └── landing/
│   │       └── landing.html        # Landing page template
│   ├── __init__.py
│   ├── admin.py                    # Admin configuration
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Data models
│   ├── tests.py                    # Unit tests
│   ├── urls.py                     # App URLs
│   └── views.py                    # View functions
│
├── theme/                           # Tailwind theme app
│   ├── static/
│   │   └── css/
│   │       └── dist/               # Compiled CSS
│   ├── static_src/
│   │   ├── src/
│   │   │   └── styles.css         # Source CSS
│   │   ├── package.json           # Node dependencies
│   │   ├── postcss.config.js      # PostCSS config
│   │   └── tailwind.config.js     # Tailwind config
│   ├── templates/
│   │   └── base.html              # Base template
│   ├── __init__.py
│   └── apps.py
│
├── db.sqlite3                       # SQLite database
├── manage.py                        # Django CLI
├── requirements.txt                 # Python dependencies
├── README.md                        # Project README
├── DOCUMENTATION.md                 # This file
├── UI_UX_IMPROVEMENTS.md           # UI/UX documentation
└── development_tracking.md         # Development notes
```

---

## 9. Configuration

### Environment-Specific Settings

#### Development (`settings.py`)
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Production (recommended)
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sre_db',
        'USER': 'sre_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
```

### Email Configuration

```python
# For production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

---

## 10. Deployment Guide

### Deployment Checklist

1. **Prepare Application**
   ```bash
   # Update settings for production
   DEBUG = False
   
   # Collect static files
   python manage.py collectstatic
   
   # Run migrations
   python manage.py migrate
   
   # Build Tailwind CSS
   python manage.py tailwind build
   ```

2. **Configure Web Server (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /static/ {
           alias /path/to/staticfiles/;
       }
       
       location /media/ {
           alias /path/to/media/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Set Up WSGI Server (Gunicorn)**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   
   # Run with Gunicorn
   gunicorn Student_Resource_Exchange.wsgi:application \
       --bind 0.0.0.0:8000 \
       --workers 3
   ```

4. **Configure Systemd Service**
   ```ini
   [Unit]
   Description=Student Resource Exchange
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/project
   ExecStart=/path/to/venv/bin/gunicorn \
       --workers 3 \
       --bind unix:/path/to/project/sre.sock \
       Student_Resource_Exchange.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for Tailwind
RUN apt-get update && apt-get install -y nodejs npm

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install Tailwind dependencies
RUN python manage.py tailwind install

# Build static files
RUN python manage.py collectstatic --noinput
RUN python manage.py tailwind build

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "Student_Resource_Exchange.wsgi:application", \
     "--bind", "0.0.0.0:8000"]
```

---

## 11. Troubleshooting

### Common Issues

#### 1. Tailwind CSS Not Building

**Problem**: CSS changes not reflecting
**Solution**:
```bash
# Clear npm cache
cd theme/static_src
npm cache clean --force

# Reinstall dependencies
python manage.py tailwind install

# Rebuild CSS
python manage.py tailwind build
```

#### 2. Static Files Not Loading

**Problem**: 404 errors for static files
**Solution**:
```bash
# Collect static files
python manage.py collectstatic --clear

# Check STATIC_ROOT in settings.py
# Verify web server configuration
```

#### 3. Database Migration Issues

**Problem**: Migration conflicts
**Solution**:
```bash
# Show migrations
python manage.py showmigrations

# Fake migration if needed
python manage.py migrate --fake landing 0001

# Or reset migrations
python manage.py migrate landing zero
```

#### 4. Alpine.js Not Working

**Problem**: Mobile menu not functioning
**Solution**:
- Check Alpine.js CDN is loading
- Verify `x-data` directive on parent element
- Check browser console for JavaScript errors
- Ensure proper `x-cloak` styling

---

## 12. Development Workflow

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add: Description of changes"

# Push to remote
git push origin feature/new-feature

# Create pull request
# After review and merge, update main
git checkout main
git pull origin main
```

### Commit Message Convention

- `Add:` New feature or file
- `Fix:` Bug fix
- `Update:` Modify existing feature
- `Remove:` Delete feature or file
- `Docs:` Documentation changes
- `Style:` Code style changes
- `Refactor:` Code refactoring

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test landing

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Quality

```bash
# Format code with black
black .

# Check with flake8
flake8 .

# Type checking with mypy
mypy .
```

---

## Appendix

### A. Useful Commands

```bash
# Django management commands
python manage.py startapp appname        # Create new app
python manage.py makemigrations          # Create migrations
python manage.py migrate                 # Apply migrations
python manage.py createsuperuser         # Create admin user
python manage.py shell                   # Django shell
python manage.py dbshell                 # Database shell

# Tailwind commands
python manage.py tailwind install        # Install Tailwind
python manage.py tailwind start          # Watch mode
python manage.py tailwind build          # Production build

# Development
python manage.py runserver              # Start dev server
python manage.py runserver 0.0.0.0:8000 # Expose to network
```

### B. External Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [DaisyUI Components](https://daisyui.com/)

### C. Version History

- **v0.1.0** (2025-10-17) - Initial project setup
  - Landing page implementation
  - Tailwind CSS integration
  - Responsive design

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Maintained By**: Student Resource Exchange Team
