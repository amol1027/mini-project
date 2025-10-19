# 📖 Student Resource Exchange - Technical Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Backend Services](#backend-services)
7. [Authentication & Authorization](#authentication--authorization)
8. [User Registration System](#user-registration-system)
9. [Products Marketplace System](#products-marketplace-system)
10. [File Structure](#file-structure)
11. [Configuration](#configuration)
12. [Deployment Guide](#deployment-guide)
13. [Troubleshooting](#troubleshooting)
14. [Development Workflow](#development-workflow)

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

### Database Configuration

- **Database Name**: `db.sqlite3`
- **Location**: `d:\projects\mini project\db.sqlite3`
- **Type**: SQLite3 (Development), PostgreSQL (Production Recommended)

### Current Models

#### User Model (Custom Registration Model)
**Location**: `registration/models.py`

```python
User (Table: registration_user)
├── id (Primary Key, AutoField)
├── email (EmailField, unique, indexed)
├── password_hash (CharField, 128 chars)
├── college_id (CharField, 100 chars)
├── name (CharField, 255 chars, optional)
├── college_name (CharField, 255 chars, optional) [NEW]
├── university_name (CharField, 255 chars, optional) [NEW]
├── rating (DecimalField, max_digits=3, decimal_places=2, default=0.0)
├── email_verified (BooleanField, default=False)
├── is_admin (BooleanField, default=False)
├── address_line1 (CharField, 255 chars, optional)
├── address_line2 (CharField, 255 chars, optional)
├── city (CharField, 100 chars, optional)
├── state_province (CharField, 100 chars, optional)
├── zip_postal_code (CharField, 20 chars, optional)
├── country (CharField, 100 chars, optional)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)

Methods:
├── set_password(raw_password) - Hash and store password
├── check_password(raw_password) - Verify password
└── __str__() - Returns email

Total Fields: 14 (tracked for profile completion)
```

**Security Features**:
- Passwords hashed using Django's PBKDF2 algorithm (260,000 iterations)
- Email field is unique and indexed for fast lookups
- CSRF protection enabled on all forms
- SQL injection protection via Django ORM

#### Product Model (Marketplace)
**Location**: `products/models.py`

```python
Product (Table: products_product)
├── id (Primary Key, AutoField)
├── title (CharField, max_length=200)
├── description (TextField)
├── price (DecimalField, max_digits=10, decimal_places=2)
├── category (CharField, max_length=20, choices=[
│   'books', 'notes', 'electronics', 'stationery', 'lab_equipment'
│   ])
├── condition (CharField, max_length=20, choices=[
│   'new', 'like_new', 'good', 'fair', 'poor'
│   ])
├── seller (ForeignKey → User, on_delete=CASCADE)
├── is_available (BooleanField, default=True)
├── views (IntegerField, default=0)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)

Methods:
├── increment_views() - Increment view counter
├── get_category_display() - Return human-readable category
├── get_condition_display() - Return human-readable condition
└── __str__() - Returns title

Categories:
├── books - Books
├── notes - Notes
├── electronics - Electronics
├── stationery - Stationery
└── lab_equipment - Lab Equipment

Conditions:
├── new - New
├── like_new - Like New
├── good - Good
├── fair - Fair
└── poor - Poor
```

### Database Relationships

```
User ──┐
       │ 1:N
       ├──────> Product (as seller)
       │
       │ (Future Relationships)
       │ 1:N
       ├──────> Transaction (as buyer)
       │ 1:N
       ├──────> Transaction (as seller)
       │ 1:N
       └──────> Review (as reviewer/reviewee)
       └──────> Review (as reviewer/reviewee) (planned)

Resource ──> Transaction (1:N) (planned)
Transaction ──> Review (1:1 or 1:2) (planned)
```

### Database Indexes

- **user.email** - B-tree index for fast email lookups and uniqueness enforcement

---

## 4. API Endpoints

### Current Endpoints

#### Landing Page
- **GET** `/` - Display landing page
  - Template: `landing/landing.html`
  - Context: None
  - Authentication: Not required

#### Registration
- **GET** `/register/` - Display registration form
  - Template: `registration/register.html`
  - Context: `{'form': RegistrationForm()}`
  - Authentication: Not required
  
- **POST** `/register/` - Process user registration
  - Template: `registration/register.html`
  - Form Data Required:
    - `email` (required, unique)
    - `password` (required, min 8 chars)
    - `confirm_password` (required, must match password)
    - `college_id` (required)
    - `college_name` (required)
    - `university_name` (required)
    - `name` (optional)
    - `address_line1` (optional)
    - `address_line2` (optional)
    - `city` (optional)
    - `state_province` (optional)
    - `zip_postal_code` (optional)
    - `country` (optional)
  - Success: Redirect to `/login/` with success message
  - Failure: Re-render form with error messages
  - Authentication: Not required

#### Login
- **GET** `/login/` - Display login form
  - Template: `login/login.html`
  - Context: `{'form': LoginForm()}`
  - Authentication: Not required
  
- **POST** `/login/` - Process user login
  - Form Data: `email`, `password`, `remember_me` (optional)
  - Success Redirect:
    - Admin users → `/dashboard/`
    - Regular users → `/products/`
  - Failure: Re-render with error message
  - Sets session: `user_id`, `user_name`, `user_email`, `is_admin`
  - Authentication: Not required

#### Logout
- **GET** `/logout/` - Logout user
  - Clears all session data
  - Redirects to `/login/` with success message
  - Authentication: Required (session)

#### Products
- **GET** `/products/` - Browse products marketplace
  - Template: `products/product_list.html`
  - Query Parameters:
    - `search` - Full-text search in title/description
    - `category` - Filter by category (books, notes, electronics, stationery, lab_equipment)
  - Context: `{'products': QuerySet, 'search_query': str, 'selected_category': str}`
  - Authentication: Not required (limited view for anonymous users)

- **GET** `/products/<int:product_id>/` - View product details
  - Template: `products/product_detail.html`
  - Context: `{'product': Product, 'related_products': QuerySet}`
  - Features:
    - Increments view counter automatically
    - Shows full seller info if logged in
    - Shows limited seller info (name, college) if anonymous
    - Displays related products (same category, max 4)
  - Authentication: Not required (privacy controls apply)

#### User Profile
- **GET** `/profile/` - View user profile
  - Template: `user_profile/profile.html`
  - Context: User data with profile completion percentage and stroke_offset
  - Authentication: Required (session)
  - Redirect: `/login/` if not authenticated

#### Admin Dashboard
- **GET** `/dashboard/` - Admin overview
  - Template: `dashboard/dashboard.html`
  - Context: User statistics and analytics
  - Authentication: Required (admin only)
  - Access Control: Redirects non-admin to `/profile/`

- **GET** `/dashboard/users/` - List all users
  - Template: `dashboard/user_list.html`
  - Query Parameters: `search` - Search by email, name, or college ID
  - Context: `{'users': QuerySet, 'search_query': str}`
  - Authentication: Required (admin only)

- **GET** `/dashboard/users/<int:user_id>/` - View user details
  - Template: `dashboard/user_detail.html`
  - Context: Complete user information including college/university
  - Authentication: Required (admin only)
    - `zip_postal_code` (optional)
    - `country` (optional)
  - Validation:
    - Email format validation
    - Email uniqueness check
    - Password matching validation
    - Minimum password length (8 characters)
  - Success: Redirects to registration page with success message
  - Failure: Returns form with error messages
  - Authentication: Not required

#### Admin Panel
- **GET** `/admin/` - Django admin interface
  - Manage users, view registrations
  - Authentication: Admin user required

### Planned API Endpoints

#### Authentication
- **POST** `/api/auth/login/` - User login (planned)
- **POST** `/api/auth/logout/` - User logout (planned)
- **POST** `/api/auth/password-reset/` - Password reset (planned)
- **POST** `/api/auth/verify-email/` - Email verification (planned)

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

#### Registration Page Components

1. **Header Section**
   - Page title: "Create Your Account"
   - Subtitle: "Join the Student Resource Exchange community"
   - Gradient background

2. **Registration Form Card**
   - White card with rounded corners and shadow
   - Form sections:
     - **Account Information** (required):
       - Email address field
       - College ID field
       - Full name field (optional)
       - Password field
       - Confirm password field
     - **Address Information** (all optional):
       - Address line 1
       - Address line 2
       - City and State/Province (2-column grid)
       - ZIP/Postal code and Country (2-column grid)

3. **Form Features**
   - Real-time validation
   - Error message display
   - Success message display
   - Required field indicators (*)
   - Helpful placeholder text
   - Password strength requirements
   - Responsive grid layout

4. **Submit Section**
   - Full-width "Register" button
   - Gradient background with hover effects
   - Transform animation on hover

5. **Footer Links**
   - "Already have an account?" link
   - Sign in redirection

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

#### Registration App
```python
# models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    """Custom User model for Student Resource Exchange"""
    email = models.EmailField(unique=True, db_index=True, max_length=255)
    password_hash = models.CharField(max_length=128)
    college_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(default=0)
    email_verified = models.BooleanField(default=False)
    
    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    zip_postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password is correct"""
        return check_password(raw_password, self.password_hash)

# forms.py
from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    """Registration form for new users"""
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['email', 'college_id', 'name', 'address_line1', 
                  'address_line2', 'city', 'state_province', 
                  'zip_postal_code', 'country']
    
    def clean(self):
        """Validate password matching"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered!")
        return email

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful!')
            return redirect('registration:register')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
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

#### User Registration (Implemented)

**Registration Flow:**
1. User accesses `/register/` endpoint
2. User fills out registration form with:
   - Required: Email, Password, Confirm Password, College ID
   - Optional: Name, Address fields
3. Form validation:
   - Email format validation
   - Email uniqueness check
   - Password minimum length (8 characters)
   - Password matching validation
4. Password hashing using Django's PBKDF2 (260,000 iterations)
5. User record created in database
6. Success message displayed
7. User can proceed to login (planned)

**Security Features:**
- CSRF protection on all forms
- Password hashing with salt
- Email uniqueness enforcement
- SQL injection protection via ORM
- XSS protection in templates

**User Model Fields:**
- `email` - Unique identifier (indexed)
- `password_hash` - Securely hashed password
- `college_id` - College identification
- `name` - Full name (optional)
- `rating` - User rating system (default: 0)
- `email_verified` - Email verification status (default: False)
- Address fields (all optional)
- `created_at`, `updated_at` - Automatic timestamps

### Planned Implementation

#### Login Flow (To Be Implemented)

1. User submits credentials (email + password)
2. Authenticate against database using `check_password()`
3. Create session
4. Set session cookie
5. Redirect to dashboard

#### Permission Levels

- **Anonymous**: View public resources only
- **Student**: Full access to platform features
- **Moderator**: Can moderate content and reviews
- **Admin**: Full system access

---

## 8. User Registration System

### Overview

The registration system allows new users to create accounts on the Student Resource Exchange platform. It implements secure user registration with comprehensive validation and data collection.

### Features

#### 8.1 User Registration Form

**URL**: `http://localhost:8000/register/`

**Required Fields**:
- Email Address (validated for format and uniqueness)
- Password (minimum 8 characters)
- Confirm Password (must match password)
- College ID

**Optional Fields**:
- Full Name
- Address Line 1
- Address Line 2
- City
- State/Province
- ZIP/Postal Code
- Country

#### 8.2 Form Validation

**Email Validation**:
- Must be valid email format
- Must be unique (not already registered)
- Case-insensitive comparison
- Database index for fast lookup

**Password Validation**:
- Minimum 8 characters
- Must match confirmation field
- Hashed using PBKDF2 with 260,000 iterations
- Salt automatically added

**Required Field Validation**:
- Email, Password, Confirm Password, and College ID are mandatory
- Form submission blocked if any required field is empty

#### 8.3 Security Implementation

**Password Security**:
```python
# Password hashing
user.set_password(raw_password)
# Uses Django's PBKDF2 algorithm with:
# - 260,000 iterations
# - Automatic salt generation
# - SHA256 hash function

# Password verification
user.check_password(raw_password)
# Returns True if password matches
```

**Additional Security**:
- CSRF tokens on all forms
- SQL injection protection via Django ORM
- XSS protection in templates
- Session security
- Secure password storage (never plain text)

#### 8.4 Database Storage

**Table**: `user`  
**Database**: `sre1027.sqlite3`

**User Model Schema**:
```sql
CREATE TABLE "user" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "email" varchar(255) NOT NULL UNIQUE,
    "password_hash" varchar(128) NOT NULL,
    "college_id" varchar(100) NOT NULL,
    "name" varchar(255) NULL,
    "rating" integer NOT NULL DEFAULT 0,
    "email_verified" bool NOT NULL DEFAULT 0,
    "address_line1" varchar(255) NULL,
    "address_line2" varchar(255) NULL,
    "city" varchar(100) NULL,
    "state_province" varchar(100) NULL,
    "zip_postal_code" varchar(20) NULL,
    "country" varchar(100) NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);
CREATE INDEX "user_email" ON "user" ("email");
```

#### 8.5 Admin Panel Integration

**Access**: `http://localhost:8000/admin/registration/user/`

**Features**:
- View all registered users
- Search by email, college ID, or name
- Filter by:
  - Email verification status
  - Registration date
  - Country
- Organized fieldsets:
  - Account Information
  - Address Information (collapsible)
  - Timestamps (collapsible, read-only)
- Bulk actions available

**Admin List View**:
- Email
- College ID
- Name
- Rating
- Email Verified Status
- Registration Date

#### 8.6 User Experience

**Registration Flow**:
1. User navigates to `/register/`
2. Fills out registration form
3. Submits form
4. System validates data
5. If valid:
   - Password hashed
   - User created in database
   - Success message displayed
   - User can proceed to login (when implemented)
6. If invalid:
   - Form redisplayed with values
   - Error messages shown
   - User corrects and resubmits

**UI/UX Features**:
- Gradient background for visual appeal
- Clean white card design
- Responsive layout (mobile-friendly)
- Clear error messages
- Success feedback
- Required field indicators (*)
- Helpful placeholder text
- Password requirements displayed
- Two-column grid for address fields
- Smooth animations and transitions

#### 8.7 Testing

**Test Script**: `test_registration.py`

**Usage**:
```bash
python test_registration.py
```

**Test Coverage**:
- User creation
- Password hashing
- Password verification
- Database storage
- Model methods

**Manual Testing Checklist**:
- [ ] Access registration page
- [ ] Submit empty form (should show errors)
- [ ] Submit with mismatched passwords (should show error)
- [ ] Submit with existing email (should show error)
- [ ] Submit with short password (should show error)
- [ ] Submit with all valid required fields (should succeed)
- [ ] Submit with all fields filled (should succeed)
- [ ] Verify user appears in admin panel
- [ ] Verify password is hashed in database
- [ ] Test responsive design on mobile

#### 8.8 Future Enhancements

**Planned Features**:
- Email verification system
- Password strength indicator
- Social authentication (Google, GitHub)
- Two-factor authentication (2FA)
- Profile picture upload
- Password recovery
- Account activation link
- CAPTCHA for bot prevention
- Terms of service acceptance
- Privacy policy acceptance

### Code Examples

**Creating a User Programmatically**:
```python
from registration.models import User

# Create user
user = User()
user.email = "student@college.edu"
user.college_id = "STU12345"
user.name = "John Doe"
user.set_password("securepassword123")
user.address_line1 = "123 Main St"
user.city = "College Town"
user.save()
```

**Querying Users**:
```python
# Get all users
all_users = User.objects.all()

# Get user by email
user = User.objects.get(email="student@college.edu")

# Filter verified users
verified = User.objects.filter(email_verified=True)

# Count users
total = User.objects.count()
```

**Verifying Password**:
```python
user = User.objects.get(email="student@college.edu")
if user.check_password("password123"):
    print("Password correct!")
else:
    print("Invalid password")
```

---

## 9. Products Marketplace System

### 9.1 Overview

The Products Marketplace is a core feature that allows students to list, browse, search, and purchase educational resources from other students. It includes product categories, search functionality, privacy controls, and comprehensive product details.

### 9.2 Product Model

**Location**: `products/models.py`

```python
class Product(models.Model):
    # Categories
    CATEGORY_CHOICES = [
        ('books', 'Books'),
        ('notes', 'Notes'),
        ('electronics', 'Electronics'),
        ('stationery', 'Stationery'),
        ('lab_equipment', 'Lab Equipment'),
    ]
    
    # Conditions
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    # Fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    seller = models.ForeignKey('registration.User', on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 9.3 Views

#### Product List View
**Location**: `products/views.py`

```python
def product_list(request):
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Category filtering
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category=category)
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'search_query': search_query,
        'selected_category': category,
    })
```

#### Product Detail View
**Location**: `products/views.py`

```python
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Increment view counter
    product.views += 1
    product.save()
    
    # Get related products (same category, different seller)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })
```

### 9.4 URL Patterns

**Location**: `products/urls.py`

```python
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
]
```

### 9.5 Templates

#### Product List Template
**Location**: `products/templates/products/product_list.html`

**Features**:
- Responsive grid layout (1-4 columns based on screen size)
- Search bar with icon
- Category filter buttons
- Product cards with hover effects
- User dropdown navigation (Alpine.js)
- Login/Logout buttons
- Product count display

**Key Components**:
- Search form with GET method
- Category links with active state highlighting
- Product cards showing:
  - Category emoji icon
  - Title (truncated to 2 lines)
  - Description (truncated to 2 lines)
  - Price in INR (₹)
  - Condition badge
  - View count
  - Seller name (truncated)

#### Product Detail Template
**Location**: `products/templates/products/product_detail.html`

**Features**:
- Two-column layout (product info + seller info)
- Large product icon/placeholder
- Comprehensive product details
- Privacy-aware seller information
- Related products carousel
- Breadcrumb navigation

**Privacy Controls**:
- **Logged In Users**: See full seller details (email, university, rating)
- **Anonymous Users**: See limited info (name, college only) with login prompt

**Seller Information Display**:
```django
{% if request.session.user_id %}
    <!-- Full seller information -->
    <div>Email: {{ product.seller.email }}</div>
    <div>University: {{ product.seller.university_name }}</div>
    <div>Rating: {{ product.seller.rating }}/5</div>
    <button>Contact Seller</button>
{% else %}
    <!-- Limited information with login prompt -->
    <div>Seller: {{ product.seller.name }}</div>
    <div class="login-prompt">
        Login to view full seller details
        <a href="{% url 'login:login' %}">Login to Continue</a>
    </div>
    <button disabled>Login to Contact Seller</button>
{% endif %}
```

### 9.6 Management Commands

#### Create Sample Products
**Location**: `products/management/commands/create_sample_products.py`

**Purpose**: Generate 10 diverse product listings for testing and demonstration

**Usage**:
```bash
python manage.py create_sample_products
```

**Sample Data Generated**:
- 2 Books (Data Structures, Physics textbook)
- 2 Notes (Machine Learning, Organic Chemistry)
- 2 Electronics (Graphing calculator, USB drive)
- 2 Stationery (Scientific calculator, Geometry set)
- 2 Lab Equipment (Digital multimeter, Microscope slides)

**Features**:
- Realistic product titles and descriptions
- Varied pricing (₹50 - ₹2499)
- Different conditions (new, like_new, good)
- Assigned to first available user as seller
- All products marked as available

### 9.7 Admin Integration

**Location**: `products/admin.py`

```python
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'seller', 'is_available', 'views', 'created_at']
    list_filter = ['category', 'condition', 'is_available', 'created_at']
    search_fields = ['title', 'description', 'seller__email', 'seller__name']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Product Information', {
            'fields': ['title', 'description', 'price']
        }),
        ('Classification', {
            'fields': ['category', 'condition']
        }),
        ('Seller & Availability', {
            'fields': ['seller', 'is_available']
        }),
        ('Statistics', {
            'fields': ['views', 'created_at', 'updated_at']
        }),
    ]
```

**Admin Features**:
- List view with sortable columns
- Filters by category, condition, availability, date
- Search by title, description, seller email/name
- Organized fieldsets for easy editing
- Read-only fields for statistics

### 9.8 Features & Functionality

#### Search & Filtering
- **Full-text search**: Searches in title and description fields
- **Category filters**: 5 categories with emoji icons
- **Active state**: Highlights selected category
- **URL parameters**: Search and category persist in URL
- **Empty state**: Friendly message when no products found

#### Privacy & Security
- **Anonymous users**: See seller name and college only
- **Logged-in users**: See full contact details (email, university, rating)
- **Login prompts**: Beautiful gradient CTA boxes encourage registration
- **Blurred preview**: Shows placeholder of hidden information
- **Disabled buttons**: Contact button disabled for anonymous users

#### User Experience
- **View counter**: Automatically increments on each product view
- **Related products**: Shows 4 similar items from same category
- **Responsive design**: Mobile-first with adaptive layouts
- **Smooth animations**: Hover effects and transitions
- **Loading states**: Proper handling of empty states

#### Navigation
- **Breadcrumbs**: Easy navigation back to product list
- **User dropdown**: Avatar-based menu with Alpine.js
- **Quick links**: Home, Profile, Dashboard (admin), Logout
- **Login redirect**: After login, redirects to products page

### 9.9 Database Queries

**Get all available products**:
```python
products = Product.objects.filter(is_available=True)
```

**Search products**:
```python
from django.db.models import Q
products = Product.objects.filter(
    Q(title__icontains=query) | Q(description__icontains=query)
)
```

**Get products by category**:
```python
books = Product.objects.filter(category='books')
```

**Get seller's products**:
```python
user_products = Product.objects.filter(seller=user, is_available=True)
```

**Get related products**:
```python
related = Product.objects.filter(
    category=product.category,
    is_available=True
).exclude(id=product.id)[:4]
```

**Most viewed products**:
```python
popular = Product.objects.filter(is_available=True).order_by('-views')[:10]
```

### 9.10 Testing

**Unit Tests**:
```python
from django.test import TestCase
from products.models import Product
from registration.models import User

class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="seller@test.com",
            college_id="TEST123"
        )
        
    def test_create_product(self):
        product = Product.objects.create(
            title="Test Book",
            description="Test Description",
            price=500.00,
            category="books",
            condition="good",
            seller=self.user
        )
        self.assertEqual(product.title, "Test Book")
        self.assertEqual(product.views, 0)
        self.assertTrue(product.is_available)
```

**Manual Testing Checklist**:
- [ ] Browse products as anonymous user
- [ ] Search for products
- [ ] Filter by each category
- [ ] View product details (anonymous)
- [ ] Verify limited seller info for anonymous users
- [ ] Login and view product details
- [ ] Verify full seller info for logged-in users
- [ ] Test view counter increments
- [ ] Check related products appear
- [ ] Test responsive design on mobile
- [ ] Verify admin can manage products

### 9.11 Future Enhancements

**Planned Features**:
- Image uploads for products
- User ability to post products
- Edit and delete own products
- Favorites/wishlist functionality
- Product reviews and ratings
- Direct messaging between buyers and sellers
- Transaction history
- Payment integration
- Product status (sold, reserved, available)
- Advanced filters (price range, location, seller rating)
- Sorting options (price, date, popularity)
- Bulk product upload for admin

---

## 10. File Structure

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
├── registration/                    # User registration app
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py        # Initial User model migration
│   │   ├── 0002_user_rating.py    # Added rating field
│   │   └── 0003_user_college_name_user_university_name.py  # Added college/university
│   ├── templates/
│   │   └── registration/
│   │       └── register.html      # Registration form template
│   ├── __init__.py
│   ├── admin.py                    # User admin configuration
│   ├── apps.py                     # App configuration
│   ├── forms.py                    # RegistrationForm (14 fields)
│   ├── models.py                   # User model (14 fields)
│   ├── tests.py                    # Unit tests
│   ├── urls.py                     # Registration URLs
│   ├── views.py                    # Registration views
│   └── README.md                   # Registration app docs
│
├── login/                           # Authentication app
│   ├── templates/
│   │   └── login/
│   │       └── login.html         # Login page
│   ├── __init__.py
│   ├── forms.py                    # LoginForm
│   ├── views.py                    # Login/logout (redirects to products)
│   └── urls.py                     # Login URLs
│
├── products/                        # Products marketplace app
│   ├── management/
│   │   └── commands/
│   │       └── create_sample_products.py  # Generate 10 sample products
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py        # Product model migration
│   ├── templates/
│   │   └── products/
│   │       ├── product_list.html  # Browse products page
│   │       └── product_detail.html # Product detail page
│   ├── __init__.py
│   ├── admin.py                    # Product admin configuration
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Product model (categories, conditions)
│   ├── tests.py                    # Unit tests
│   ├── urls.py                     # Product URLs
│   └── views.py                    # Product list & detail views
│
├── dashboard/                       # Admin dashboard app
│   ├── templates/
│   │   └── dashboard/
│   │       ├── dashboard.html     # Admin overview
│   │       ├── user_list.html     # User management
│   │       └── user_detail.html   # User details (incl. college/university)
│   ├── templatetags/
│   │   └── dashboard_filters.py   # Custom template filters
│   ├── __init__.py
│   ├── views.py                    # Dashboard views
│   └── urls.py                     # Dashboard URLs
│
├── user_profile/                    # User profile app
│   ├── templates/
│   │   └── user_profile/
│   │       └── profile.html       # Profile page (14-field completion)
│   ├── __init__.py
│   ├── views.py                    # Profile view (calculates stroke_offset)
│   └── urls.py                     # Profile URLs
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
│   │   └── base.html              # Base template (auto-dismiss messages)
│   ├── __init__.py
│   └── apps.py
│
├── db.sqlite3                       # SQLite database
├── manage.py                        # Django CLI
├── requirements.txt                 # Python dependencies
├── README.md                        # Project README
├── DOCUMENTATION.md                 # This file (comprehensive technical docs)
└── UI_UX_IMPROVEMENTS.md           # UI/UX changelog
```

---

## 9. Configuration

### Environment-Specific Settings

#### Development (`settings.py`)
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'sre1027.sqlite3',  # Custom database name
    }
}

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'theme',
    'landing',
    'registration',  # User registration app
]
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

#### 5. Registration Form Issues

**Problem**: "Email already registered" error
**Solution**:
```python
# Check existing users in Django shell
python manage.py shell
>>> from registration.models import User
>>> User.objects.filter(email="email@example.com")
# Delete duplicate if needed
>>> User.objects.filter(email="email@example.com").delete()
```

**Problem**: Password not saving
**Solution**:
- Ensure `set_password()` method is called before `save()`
- Check that password field is named `password_hash` in model
- Verify form is using `commit=False` before setting password

**Problem**: 404 on `/register/`
**Solution**:
```python
# Verify registration app is in INSTALLED_APPS
# Check urls.py includes registration.urls
# Restart development server
python manage.py runserver
```

**Problem**: Database errors
**Solution**:
```bash
# Run migrations
python manage.py makemigrations registration
python manage.py migrate

# If database is corrupted, recreate
rm sre1027.sqlite3
python manage.py migrate
```

#### 6. Admin Panel Issues

**Problem**: Cannot access admin panel
**Solution**:
```bash
# Create superuser
python manage.py createsuperuser

# Verify admin is registered in admin.py
# Check URL: http://localhost:8000/admin/
```

#### 7. Form Validation Not Working

**Problem**: Form submits with invalid data
**Solution**:
- Check `clean()` method in forms.py
- Verify `form.is_valid()` is called in view
- Ensure CSRF token is present in template
- Check browser console for JavaScript errors

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
python manage.py test registration

# Run registration test script
python test_registration.py

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Registration-Specific Commands

```bash
# View all registered users
python manage.py shell
>>> from registration.models import User
>>> User.objects.all()

# Count registered users
>>> User.objects.count()

# Get user by email
>>> user = User.objects.get(email="test@example.com")
>>> print(user.name, user.college_id)

# Verify password
>>> user.check_password("password123")

# Create user programmatically
>>> user = User()
>>> user.email = "new@example.com"
>>> user.college_id = "COL123"
>>> user.set_password("password")
>>> user.save()

# Delete all users (careful!)
>>> User.objects.all().delete()

# Check database directly
python manage.py dbshell
> .tables
> SELECT * FROM user;
> .exit
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

# Registration-specific commands
python test_registration.py              # Test registration system
python manage.py shell                   # Access User model
python manage.py migrate registration    # Run registration migrations

# Tailwind commands
python manage.py tailwind install        # Install Tailwind
python manage.py tailwind start          # Watch mode
python manage.py tailwind build          # Production build

# Development
python manage.py runserver              # Start dev server
python manage.py runserver 0.0.0.0:8000 # Expose to network

# Database management
python manage.py showmigrations         # Show migration status
python manage.py sqlmigrate app_name 0001  # Show SQL for migration
python manage.py flush                  # Clear all data (dangerous!)
```

### B. External Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [DaisyUI Components](https://daisyui.com/)

### C. Version History

- **v0.2.0** (2025-10-17) - User Registration System
  - Created `registration` app with custom User model
  - Implemented registration form with validation
  - Added password hashing with PBKDF2
  - Created beautiful registration UI with Tailwind CSS
  - Database changed to `sre1027.sqlite3`
  - Added admin panel for user management
  - Implemented form validation (email uniqueness, password matching)
  - Added address fields (optional)
  - Created comprehensive documentation

- **v0.1.0** (2025-10-17) - Initial project setup
  - Landing page implementation
  - Tailwind CSS integration
  - Responsive design

---

**Document Version**: 2.0  
**Last Updated**: October 17, 2025  
**Maintained By**: Student Resource Exchange Team
