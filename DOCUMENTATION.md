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
10. [Borrow/Lend System](#borrow-lend-system)
11. [Real-Time Chat System](#real-time-chat-system)
12. [File Structure](#file-structure)
13. [Configuration](#configuration)
14. [Deployment Guide](#deployment-guide)
15. [Troubleshooting](#troubleshooting)
16. [Development Workflow](#development-workflow)
17. [Recent UI/UX Enhancements (v1.9)](#17-recent-uiux-enhancements-v19)

---

## 1. Introduction

### Project Overview

Student Resource Exchange (SRE) is a Django-based web platform designed to facilitate the sharing and exchange of educational resources among students. The platform provides a secure, user-friendly interface for posting, browsing, borrowing, and lending academic materials.

**Current Version**: 1.9.0  
**Last Updated**: January 2025  
**Status**: Production-ready with borrow/lend system, real-time chat, and complete product lifecycle management

### Key Highlights (v1.9)

- ✅ **Borrow/Lend System** - Rental marketplace with deposit management and request workflows
- ✅ **Flexible Listings** - Sell, lend, or both options for each product
- ✅ **Rental Management** - Complete workflow from request to approval to return
- ✅ **Lender Dashboard** - Statistics and request management interface
- ✅ **Real-Time Chat System** - Messaging between buyers/sellers/borrowers/lenders
- ✅ **Smart Notifications** - Unread message badges with auto-polling updates
- ✅ **Notification Preferences** - Customizable sound, desktop, and email notifications
- ✅ **Modern Chat UI** - Clean light theme with message bubbles and smooth animations
- ✅ **Mobile Chat Optimization** - Touch-friendly interface with responsive design
- ✅ **Global Navigation System** - Unified navbar with Alpine.js-powered dropdowns
- ✅ **Smart Pagination** - 12 products per page with filter preservation
- ✅ **Enhanced Privacy** - Seller information completely hidden for guests
- ✅ **Auto-Dismiss Messages** - Floating notifications with 5-second auto-hide
- ✅ **Product Management** - Full CRUD with image upload (up to 5 images)
- ✅ **Role-Based Access** - Admin dashboard with comprehensive analytics

### Technology Stack

- **Backend**: Django 5.2.7, Python 3.13.1
- **Frontend**: Tailwind CSS 3.x, Alpine.js 3.14.0
- **Database**: SQLite (development), PostgreSQL-ready (production)
- **Authentication**: Session-based with PBKDF2 (260,000 iterations)
- **JavaScript**: Alpine.js for interactive components (15KB lightweight)

### Technology Decisions

- **Django**: Chosen for rapid development, built-in admin panel, and robust ORM
- **SQLite**: Default database for development; easily upgradable to PostgreSQL
- **Tailwind CSS**: Utility-first approach for rapid UI development and consistent design
- **Alpine.js**: Minimal JavaScript for interactive components without heavy frameworks

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
├── title (CharField, max_length=255)
├── description (TextField)
├── price (DecimalField, max_digits=10, decimal_places=2, min_value=0.01)
├── category (CharField, max_length=50, choices=[
│   'books', 'notes', 'electronics', 'stationery', 'lab_equipment', 'other'
│   ])
├── condition (CharField, max_length=20, choices=[
│   'new', 'like_new', 'good', 'fair', 'poor'
│   ])
├── image1 (ImageField, upload_to='products/<seller_id>/', blank=True, null=True)
├── image2 (ImageField, upload_to='products/<seller_id>/', blank=True, null=True)
├── image3 (ImageField, upload_to='products/<seller_id>/', blank=True, null=True)
├── image4 (ImageField, upload_to='products/<seller_id>/', blank=True, null=True)
├── image5 (ImageField, upload_to='products/<seller_id>/', blank=True, null=True)
├── seller (ForeignKey → User, on_delete=CASCADE, related_name='products')
├── is_available (BooleanField, default=True)
├── views (IntegerField, default=0, editable=False)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)

Methods:
├── get_primary_image() - Return image1 or None
├── get_all_images() - Return list of all non-null images (image1-image5)
├── has_images() - Check if product has at least one image
├── get_category_display() - Return human-readable category
├── get_condition_display() - Return human-readable condition
└── __str__() - Returns title

Image Upload:
├── Path: media/products/<seller_id>/<filename>
├── Automatic path management per seller
├── Up to 5 images per product
└── Fallback to emoji icons if no images

Categories:
├── books - Books
├── notes - Notes
├── electronics - Electronics
├── stationery - Stationery
├── lab_equipment - Lab Equipment
└── other - Other

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
       │ 1:N
       ├──────> Conversation (as user1)
       │ 1:N
       ├──────> Conversation (as user2)
       │ 1:N
       ├──────> Message (as sender)
       │ 1:1
       ├──────> NotificationPreference
       │
       │ (Future Relationships)
       │ 1:N
       ├──────> Transaction (as buyer)
       │ 1:N
       ├──────> Transaction (as seller)
       │ 1:N
       └──────> Review (as reviewer/reviewee)

Product ──┐
          │ 1:N
          └──────> Conversation (product context)

Conversation ──┐
               │ 1:N
               └──────> Message

Resource ──> Transaction (1:N) (planned)
Transaction ──> Review (1:1 or 1:2) (planned)
```

### Chat Models

#### Conversation Model
**Location**: `chat/models.py`

```python
Conversation (Table: chat_conversation)
├── id (Primary Key, AutoField)
├── user1 (ForeignKey → User, on_delete=CASCADE, related_name='conversations_as_user1')
├── user2 (ForeignKey → User, on_delete=CASCADE, related_name='conversations_as_user2')
├── product (ForeignKey → Product, on_delete=CASCADE, related_name='conversations')
├── user1_unread_count (IntegerField, default=0)
├── user2_unread_count (IntegerField, default=0)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)

Constraints:
└── unique_together = ['user1', 'user2', 'product']

Methods:
├── get_other_user(user) - Returns other participant
├── get_unread_count(user) - Returns unread count for user
├── mark_as_read(user) - Resets unread count to 0
└── get_total_unread_count(user) [static] - Total unread across all conversations
```

#### Message Model
**Location**: `chat/models.py`

```python
Message (Table: chat_message)
├── id (Primary Key, AutoField)
├── conversation (ForeignKey → Conversation, on_delete=CASCADE, related_name='messages')
├── sender (ForeignKey → User, on_delete=CASCADE)
├── content (TextField)
├── is_read (BooleanField, default=False)
└── timestamp (DateTimeField, auto_now_add)

Meta:
└── ordering = ['-timestamp']
```

#### NotificationPreference Model
**Location**: `chat/models.py`

```python
NotificationPreference (Table: chat_notificationpreference)
├── id (Primary Key, AutoField)
├── user (OneToOneField → User, on_delete=CASCADE, related_name='notification_preference')
├── enable_sound (BooleanField, default=True)
├── enable_desktop (BooleanField, default=False)
├── enable_email (BooleanField, default=False)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)
```

### Database Indexes

- **user.email** - B-tree index for fast email lookups and uniqueness enforcement
- **conversation (user1, user2, product)** - Unique constraint to prevent duplicates
- **message.timestamp** - Index for ordering messages efficiently

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
    - `category` - Filter by category (books, notes, electronics, stationery, lab_equipment, other)
  - Context: `{'products': QuerySet, 'search_query': str, 'selected_category': str}`
  - Authentication: Not required (limited view for anonymous users)

- **GET** `/products/<int:product_id>/` - View product details
  - Template: `products/product_detail.html`
  - Context: `{'product': Product, 'related_products': QuerySet, 'is_owner': bool}`
  - Features:
    - Increments view counter atomically using F() expressions
    - Shows full seller info if logged in
    - Shows limited seller info (name, college) if anonymous
    - Displays related products (same category, max 4)
    - Shows Edit/Delete buttons if user is product owner
    - Shows Contact Seller button if user is not owner
    - Displays actual uploaded images with thumbnail gallery
  - Authentication: Not required (privacy controls apply)

- **GET** `/products/create/` - Display product upload form
  - Template: `products/product_form.html`
  - Context: `{'form': ProductForm(), 'page_title': 'Upload New Product'}`
  - Authentication: Required (redirects to login if not authenticated)

- **POST** `/products/create/` - Create new product
  - Template: `products/product_form.html`
  - Form Data:
    - `title` (required, max 255 chars)
    - `description` (required)
    - `price` (required, decimal, min 0.01)
    - `category` (required, choice field)
    - `condition` (required, choice field)
    - `image1` to `image5` (optional, image files)
  - Success: Redirect to product detail page with success message
  - Failure: Re-render form with error messages
  - Authentication: Required

- **GET** `/products/<int:product_id>/edit/` - Display product edit form
  - Template: `products/product_form.html`
  - Context: `{'form': ProductForm(instance=product), 'product': Product, 'page_title': 'Edit Product', 'is_edit': True}`
  - Authorization: Must be product owner
  - Authentication: Required

- **POST** `/products/<int:product_id>/edit/` - Update product
  - Template: `products/product_form.html`
  - Form Data: Same as create
  - Success: Redirect to product detail page with success message
  - Failure: Re-render form with error messages
  - Authorization: Must be product owner
  - Authentication: Required

- **GET** `/products/<int:product_id>/delete/` - Display delete confirmation
  - Template: `products/product_confirm_delete.html`
  - Context: `{'product': Product}`
  - Authorization: Must be product owner
  - Authentication: Required

- **POST** `/products/<int:product_id>/delete/` - Delete product
  - Hard delete from database
  - Success: Redirect to product list with success message
  - Authorization: Must be product owner
  - Authentication: Required

- **GET** `/products/my-products/` - View user's own products
  - Template: `products/my_products.html`
  - Context:
    - `products`: QuerySet of user's products
    - `user`: Current user object
    - `total_products`: Total count
    - `available_count`: Count of available products
    - `total_views`: Sum of all views
    - `avg_price`: Average price of products
  - Authentication: Required

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

#### Chat System
- **GET** `/chat/conversations/` - List all user conversations
  - Template: `chat/conversation_list.html`
  - Context: `{'conversations': QuerySet}` with unread counts and last messages
  - Authentication: Required (session)
  - Features: Shows product context, online status, unread badges

- **GET** `/chat/chat/<int:user_id>/<int:product_id>/` - View or create conversation
  - Template: `chat/chat_detail.html`
  - Context: `{'conversation': obj, 'messages': QuerySet, 'other_user': User, 'product': Product}`
  - Authentication: Required (session)
  - Side Effects: Marks messages as read for current user

- **POST** `/chat/send_message/<int:conversation_id>/` - Send message (AJAX)
  - Form Data: `content` (required)
  - Response: JSON with message data
  - Authentication: Required (session)
  - Side Effects: Increments unread count for other user

- **GET** `/chat/get_messages/<int:conversation_id>/` - Get new messages (AJAX)
  - Query Parameters: `since` - Last message ID received
  - Response: JSON with array of new messages
  - Authentication: Required (session)
  - Used by: Auto-polling script (2s interval)

- **GET** `/chat/unread-count/` - Get total unread count (AJAX)
  - Response: JSON `{'unread_count': int}`
  - Authentication: Required (session)
  - Used by: Navbar badge polling script (15s interval)

- **GET** `/chat/notification-settings/` - View notification preferences
  - Template: `chat/notification_settings.html`
  - Context: `{'preference': NotificationPreference}`
  - Authentication: Required (session)

- **POST** `/chat/notification-settings/` - Update notification preferences
  - Form Data: `enable_sound`, `enable_desktop`, `enable_email` (checkboxes)
  - Success: Redirect with success message
  - Authentication: Required (session)

- **GET** `/chat/notification-preferences/` - Get preferences (AJAX)
  - Response: JSON with notification settings
  - Authentication: Required (session)
  - Used by: Chat UI to determine notification behavior

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

### Global Navigation System

#### Base Template (`base.html`)

The base template provides a global navigation bar and message system used across all pages.

**Key Features:**
1. **Global Navbar**
   - Sticky positioning (`sticky top-0 z-50`)
   - Consistent across all pages
   - Alpine.js-powered interactive menus
   - Responsive mobile/desktop layouts

2. **Smart Navigation Logic**
   - **Logo & Home Button**: 
     - Logged-in users → `/products/` (Products Marketplace)
     - Anonymous users → `/landing/` (Landing Page)
   - **Right-aligned Navigation**: Uses `ml-auto` for modern layout
   - **Context-aware Menu Items**:
     - Guest users: Only "Browse Products" button visible
     - Logged-in users: Home, Upload Product, Dashboard (admin only)
   
3. **User Dropdown Menu (Alpine.js)**
   ```html
   <div x-data="{ userMenuOpen: false }">
     <button @click="userMenuOpen = !userMenuOpen">...</button>
     <div x-show="userMenuOpen" @click.away="userMenuOpen = false">
       <!-- Dropdown items -->
     </div>
   </div>
   ```
   - My Profile
   - My Products
   - Logout
   - User avatar with initials

4. **Mobile Hamburger Menu (Alpine.js)**
   ```html
   <div x-data="{ mobileMenuOpen: false }">
     <button @click="mobileMenuOpen = !mobileMenuOpen">...</button>
     <div x-show="mobileMenuOpen">
       <!-- Mobile menu items -->
     </div>
   </div>
   ```
   - Slide-in panel from right
   - Full-height overlay
   - Touch-friendly buttons

5. **Global Message System**
   - **Position**: `fixed top-20 right-4 z-50` (floating top-right)
   - **Animation**: `fadeInUp` (0.6s ease-out)
   - **Auto-dismiss**: 5 seconds using Alpine.js
   ```html
   <div x-data="{ show: true }" 
        x-show="show" 
        x-init="setTimeout(() => show = false, 5000)">
   ```
   - **Color-coded**: Green (success), Red (error), Yellow (warning), Blue (info)
   - **Icons**: SVG icons for each message type
   - **Consistent Styling**: Border-left accent, shadow, rounded corners

**Base Template Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <!-- Meta tags, title, CSS -->
    - Tailwind CSS
    - Alpine.js 3.14.0
    - Inter Font
    - Custom animations (fadeInUp)
</head>
<body>
    <!-- Global Navbar -->
    <nav class="sticky top-0 z-50">
        <!-- Logo, Navigation, User Menu -->
    </nav>
    
    <!-- Global Messages -->
    {% if messages %}
        <!-- Floating notifications -->
    {% endif %}
    
    <!-- Page Content -->
    <main>
        {% block content %}
        {% endblock %}
    </main>
    
    <!-- Footer -->
    <footer>
        <!-- Links and copyright -->
    </footer>
</body>
</html>
```

### Page Structure

#### Landing Page Components

1. **Header/Navigation**
   - Uses global navbar from base.html
   - Smart home button routing
   - Consistent branding

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
        ('other', 'Other'),
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
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    # Images (up to 5 images per product)
    image1 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    image2 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    image3 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    image4 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    image5 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    
    seller = models.ForeignKey('registration.User', on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True)
    views = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Helper Methods
    def get_primary_image(self):
        """Return the primary image or None"""
        return self.image1 if self.image1 else None
    
    def get_all_images(self):
        """Return list of all non-null images"""
        images = []
        for i in range(1, 6):
            img = getattr(self, f'image{i}')
            if img:
                images.append(img)
        return images
    
    def has_images(self):
        """Check if product has at least one image"""
        return bool(self.image1)

# Custom upload path function
def product_image_upload_path(instance, filename):
    """Generate upload path: products/<seller_id>/<filename>"""
    ext = filename.split('.')[-1]
    filename = f"{instance.title[:50]}_{instance.id or 'new'}.{ext}"
    return os.path.join('products', str(instance.seller.id), filename)
```

**Image Management**:
- Up to 5 images per product
- Automatic path: `media/products/<seller_id>/<filename>`
- Organized by seller for easy management
- Fallback to emoji icons if no images uploaded

### 9.3 Views

#### Product List View
**Location**: `products/views.py`

```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    
    # Pagination - 12 products per page
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        products_page = paginator.page(paginator.num_pages)
    
    return render(request, 'products/product_list.html', {
        'products_page': products_page,
        'search_query': search_query,
        'selected_category': category,
    })
```

**Pagination Features:**
- **12 products per page** for optimal performance and UX
- **Smart page navigation** with Previous/Next buttons
- **Page numbers with ellipsis** (e.g., 1 ... 5 6 7 ... 20)
- **Filter preservation** across pages (category and search persist)
- **Error handling**: Invalid pages redirect to first/last page
- **Page info display**: "Showing X to Y of Z products"
- **URL construction**: `?page=2&category=Books&search=calculus`

#### Product Detail View
**Location**: `products/views.py`

```python
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Increment view counter atomically (concurrency-safe)
    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)
    
    # Get related products (same category, different seller)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Check if current user is the owner
    is_owner = False
    if 'user_id' in request.session:
        is_owner = product.seller.id == request.session['user_id']
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'is_owner': is_owner,
    })
```

**Concurrency Safety**:
- Uses Django's `F()` expressions for atomic view counter increment
- Prevents race conditions when multiple users view simultaneously
- Database-level operation ensures accuracy

#### Product Create View
**Location**: `products/views.py`

```python
def product_create(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to upload a product.')
        return redirect('login:login')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = User.objects.get(id=request.session['user_id'])
            product.save()
            messages.success(request, f'Product "{product.title}" uploaded successfully!')
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'page_title': 'Upload New Product',
    })
```

#### Product Edit View
**Location**: `products/views.py`

```python
def product_edit(request, product_id):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to edit products.')
        return redirect('login:login')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check ownership
    if product.seller.id != request.session['user_id']:
        messages.error(request, 'You can only edit your own products.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.title}" updated successfully!')
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'page_title': 'Edit Product',
        'is_edit': True,
    })
```

#### My Products View
**Location**: `products/views.py`

```python
def my_products(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to view your products.')
        return redirect('login:login')
    
    user = User.objects.get(id=request.session['user_id'])
    products = Product.objects.filter(seller=user).order_by('-created_at')
    
    # Calculate statistics
    total_products = products.count()
    available_count = products.filter(is_available=True).count()
    total_views = sum(product.views for product in products)
    avg_price = sum(product.price for product in products) // total_products if total_products > 0 else 0
    
    return render(request, 'products/my_products.html', {
        'products': products,
        'user': user,
        'total_products': total_products,
        'available_count': available_count,
        'total_views': total_views,
        'avg_price': avg_price,
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
    path('create/', views.product_create, name='product_create'),
    path('<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('my-products/', views.my_products, name='my_products'),
]
```

**URL Access Control**:
- `/products/` - Public (browse products)
- `/products/<id>/` - Public (view details with privacy controls)
- `/products/create/` - Login required
- `/products/<id>/edit/` - Login required + Owner only
- `/products/<id>/delete/` - Login required + Owner only
- `/products/my-products/` - Login required

### 9.5 Templates

#### Product List Template
**Location**: `products/templates/products/product_list.html`

**Features**:
- Responsive grid layout (1-4 columns based on screen size)
- Search bar with icon
- Category filter buttons
- Product cards with hover effects and image zoom
- User dropdown navigation (Alpine.js)
- Login/Logout buttons
- Product count display
- Actual product images with fallback to emoji icons

**Key Components**:
- Search form with GET method
- Category links with active state highlighting
- Product cards showing:
  - Actual uploaded image or category emoji icon
  - Title (truncated to 2 lines)
  - Description (truncated to 2 lines)
  - Price in INR (₹)
  - Condition badge
  - View count
  - Seller name (truncated)
  - Hover effect with image scale animation

#### Product Detail Template
**Location**: `products/templates/products/product_detail.html`

**Features**:
- Two-column layout (product info + seller info)
- Large product image display with actual uploaded images
- Thumbnail gallery for multiple images (if more than one)
- Comprehensive product details
- Privacy-aware seller information
- Owner-specific controls (Edit/Delete for owners)
- Related products carousel with actual images
- Breadcrumb navigation

**Image Display**:
- Primary image displayed prominently (max-height: 384px)
- Thumbnail gallery below for additional images
- Fallback to category emoji if no images uploaded
- Related products show actual images with hover effects

**Privacy Controls**:
- **Logged In Users**: See full seller details (email, university, rating)
- **Anonymous Users**: See limited info (name, college only) with login prompt

**Owner Controls**:
```django
{% if is_owner %}
    <!-- Owner Actions: Edit/Delete buttons -->
    <a href="{% url 'products:product_edit' product.id %}">Edit Product</a>
    <a href="{% url 'products:product_delete' product.id %}">Delete Product</a>
    <div>This is your product listing</div>
{% elif product.is_available %}
    <!-- Non-owner: Show Contact Seller button -->
    <button>Contact Seller</button>
{% else %}
    <button disabled>Not Available</button>
{% endif %}
```

**Seller Information Display**:
```django
{% if request.session.user_id %}
    <!-- Full seller information -->
    <div>Email: {{ product.seller.email }}</div>
    <div>University: {{ product.seller.university_name }}</div>
    <div>Rating: {{ product.seller.rating }}/5</div>
    
    {% if is_owner %}
        <a href="{% url 'products:product_edit' product.id %}">Edit Product</a>
        <a href="{% url 'products:product_delete' product.id %}">Delete Product</a>
    {% else %}
        <button>Contact Seller</button>
    {% endif %}
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

#### My Products Template
**Location**: `products/templates/products/my_products.html`

**Features**:
- Dashboard-style statistics cards:
  - Total Products count
  - Available Products count
  - Total Views across all products
  - Average Price of products
- Product table with all user's listings
- Quick actions (View, Edit, Delete) for each product
- Product thumbnails in table
- Responsive design with mobile support
- Empty state with upload prompt

**Statistics Display**:
```django
<div>Total Products: {{ total_products }}</div>
<div>Available: {{ available_count }}</div>
<div>Total Views: {{ total_views }}</div>
<div>Avg. Price: ₹{{ avg_price }}</div>
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
- Image uploads for products ✅ (Completed in v1.6)
- User ability to post products ✅ (Completed in v1.6)
- Edit and delete own products ✅ (Completed in v1.6)
- Direct messaging between buyers and sellers ✅ (Completed in v1.8)
- Favorites/wishlist functionality
- Product reviews and ratings
- Transaction history
- Payment integration
- Product status (sold, reserved, available)
- Advanced filters (price range, location, seller rating)
- Sorting options (price, date, popularity)
- Bulk product upload for admin

---

## 10. Borrow/Lend System

### 10.1 Overview

The Borrow/Lend System extends the marketplace to support both selling and rental transactions. Students can list items for lending, request to borrow items, and manage rental workflows including approval, returns, and deposits.

**Key Features**:
- Flexible listing types (sell, lend, or both)
- Daily rental pricing with security deposits
- Configurable maximum borrow duration (1-90 days)
- Real-time cost calculator
- Complete request workflow (pending → approved → active → returned)
- Lender dashboard with statistics
- Borrower request tracking
- Overdue detection
- Direct borrower-lender messaging
- Product availability tracking

### 10.2 Database Models

#### Product Model Extensions
**Location**: `products/models.py`

```python
class Product(models.Model):
    # ... existing fields ...
    
    # Listing type
    LISTING_TYPE_CHOICES = [
        ('sell', 'For Sale'),
        ('lend', 'For Lending'),
        ('both', 'For Sale or Lending'),
    ]
    listing_type = models.CharField(
        max_length=10,
        choices=LISTING_TYPE_CHOICES,
        default='sell'
    )
    
    # Lending-specific fields
    borrow_price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.01)]
    )
    borrow_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    max_borrow_days = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(90)]
    )
    is_currently_borrowed = models.BooleanField(default=False)
    
    # Helper methods
    def can_be_borrowed(self):
        return self.listing_type in ['lend', 'both'] and not self.is_currently_borrowed
    
    def can_be_purchased(self):
        return self.listing_type in ['sell', 'both']
```

#### BorrowRequest Model
**Location**: `products/models.py`

```python
class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    # Relationships
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests_made')
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests_received')
    
    # Request details
    requested_days = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    lender_response = models.TextField(blank=True)
    
    # Financial
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Dates
    request_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_overdue(self):
        if self.status == 'active' and self.expected_return_date:
            return date.today() > self.expected_return_date
        return False
    
    def calculate_total_cost(self):
        if self.product.borrow_price_per_day:
            return self.requested_days * self.product.borrow_price_per_day
        return 0
```

### 10.3 Views and Workflows

#### Borrow Request Creation
**Location**: `products/views.py`

```python
@login_required
def borrow_request_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Validation
    if not product.can_be_borrowed():
        messages.error(request, 'This product is not available for borrowing.')
        return redirect('products:product_detail', product_id=product.id)
    
    if request.user == product.seller:
        messages.error(request, 'You cannot borrow your own product.')
        return redirect('products:product_detail', product_id=product.id)
    
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST, product=product)
        if form.is_valid():
            borrow_request = form.save(commit=False)
            borrow_request.product = product
            borrow_request.borrower = request.user
            borrow_request.lender = product.seller
            borrow_request.total_cost = borrow_request.calculate_total_cost()
            borrow_request.deposit_amount = product.borrow_deposit or 0
            borrow_request.save()
            
            messages.success(request, 'Borrow request submitted!')
            return redirect('products:borrow_request_detail', request_id=borrow_request.id)
```

#### Request Approval
**Location**: `products/views.py`

```python
@login_required
def borrow_request_approve(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Authorization check
    if borrow_request.lender != request.user:
        messages.error(request, 'You are not authorized to approve this request.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if borrow_request.status != 'pending':
        messages.error(request, 'This request cannot be approved.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        
        borrow_request.status = 'approved'
        borrow_request.approved_date = timezone.now()
        borrow_request.start_date = start_date
        borrow_request.expected_return_date = (
            datetime.strptime(start_date, '%Y-%m-%d').date() +
            timedelta(days=borrow_request.requested_days)
        )
        borrow_request.product.is_currently_borrowed = True
        borrow_request.product.save()
        borrow_request.save()
        
        messages.success(request, 'Borrow request approved!')
```

### 10.4 Templates

#### Borrow Request Form
**Location**: `products/templates/products/borrow_request_create.html`

**Features**:
- Product details display
- Number of days selector
- Real-time cost calculator using Alpine.js
- Deposit information
- Optional message to lender
- Cost breakdown: daily rate × days + deposit

**JavaScript Cost Calculator**:
```javascript
x-data="{
    days: 1,
    dailyRate: {{ product.borrow_price_per_day }},
    deposit: {{ product.borrow_deposit|default:0 }},
    get totalCost() {
        return (this.days * this.dailyRate) + this.deposit;
    }
}"
```

#### Lender Dashboard
**Location**: `products/templates/products/my_lend_requests.html`

**Features**:
- Statistics cards: Total requests, Active borrows, Completed, Pending
- Color-coded status badges
- Quick action buttons (Approve/Reject)
- Request filtering by status
- Borrower information with contact link
- Date tracking

### 10.5 URL Patterns

**Location**: `products/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    
    # Borrow/Lend routes
    path('products/<int:product_id>/borrow/', borrow_request_create, name='borrow_request_create'),
    path('products/borrow-requests/<int:request_id>/', borrow_request_detail, name='borrow_request_detail'),
    path('products/borrow-requests/<int:request_id>/approve/', borrow_request_approve, name='borrow_request_approve'),
    path('products/borrow-requests/<int:request_id>/reject/', borrow_request_reject, name='borrow_request_reject'),
    path('products/borrow-requests/<int:request_id>/return/', borrow_request_return, name='borrow_request_return'),
    path('products/borrow-requests/<int:request_id>/cancel/', borrow_request_cancel, name='borrow_request_cancel'),
    path('products/my-borrow-requests/', my_borrow_requests, name='my_borrow_requests'),
    path('products/my-lend-requests/', my_lend_requests, name='my_lend_requests'),
]
```

### 10.6 Business Logic

**Workflow States**:
1. **Pending**: Initial state when borrower submits request
2. **Approved**: Lender approves with start date
3. **Active**: Borrowing period in progress (product marked as borrowed)
4. **Returned**: Item returned by borrower (product becomes available)
5. **Rejected**: Lender declines the request
6. **Cancelled**: Borrower cancels pending request
7. **Overdue**: Active borrow past expected return date

**Validation Rules**:
- Borrower cannot be the product owner
- Product must have `can_be_borrowed()` return True
- Requested days cannot exceed `max_borrow_days`
- Product cannot be borrowed if `is_currently_borrowed` is True
- Only lender can approve/reject requests
- Only borrower can cancel pending requests
- Only active requests can be marked as returned

**Financial Calculations**:
- Total Cost = (Daily Rate × Number of Days) + Deposit
- Deposit is separate from rental cost
- Cost calculated on request creation and displayed to borrower

### 10.7 Integration with Chat

Borrowers and lenders can start conversations directly from request detail pages:

```python
# In borrow_request_detail.html
<a href="{% url 'chat:start_conversation_with_user' product_id=request.product.id other_user_id=other_user.id %}">
    Contact {{ other_user.first_name }}
</a>
```

**Chat Integration**:
- Direct messaging between borrower and lender
- Product context maintained in conversation
- Intelligent role detection (buyer/seller based on ownership)

### 10.8 Future Enhancements

- Payment integration for deposits and rental fees
- Automated overdue reminders
- Rating system for borrowers and lenders
- Insurance options for high-value items
- Calendar view for availability
- Recurring rental patterns
- Damage reporting workflow
- Dispute resolution system

---

## 11. Real-Time Chat System

### 10.1 Overview

The chat system enables real-time communication between buyers and sellers, with each conversation linked to a specific product. The system includes notification preferences, unread message tracking, and automatic polling for updates.

**Key Features**:
- Real-time messaging with 2-second polling intervals
- Unread message badges with 15-second global polling
- Customizable notification preferences (sound, desktop, email)
- Product-context conversations
- Modern light theme UI with message bubbles
- Mobile-optimized responsive design
- Online status indicators
- Automatic message read tracking

### 10.2 Database Models

#### Conversation Model
**Location**: `chat/models.py`

```python
Conversation (Table: chat_conversation)
├── id (Primary Key, AutoField)
├── user1 (ForeignKey → User, on_delete=CASCADE, related_name='conversations_as_user1')
├── user2 (ForeignKey → User, on_delete=CASCADE, related_name='conversations_as_user2')
├── product (ForeignKey → Product, on_delete=CASCADE, related_name='conversations')
├── user1_unread_count (IntegerField, default=0)
├── user2_unread_count (IntegerField, default=0)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)

Methods:
├── get_other_user(user) - Returns the other participant in the conversation
├── get_unread_count(user) - Returns unread count for the specified user
├── mark_as_read(user) - Resets unread count to 0 for the user
├── get_total_unread_count(user) [static] - Returns total unread across all user's conversations
└── __str__() - Returns "Conversation between {user1} and {user2} about {product}"

Unique Constraint: (user1, user2, product) - Prevents duplicate conversations
```

#### Message Model
**Location**: `chat/models.py`

```python
Message (Table: chat_message)
├── id (Primary Key, AutoField)
├── conversation (ForeignKey → Conversation, on_delete=CASCADE, related_name='messages')
├── sender (ForeignKey → User, on_delete=CASCADE)
├── content (TextField)
├── is_read (BooleanField, default=False)
└── timestamp (DateTimeField, auto_now_add)

Meta:
└── ordering = ['-timestamp']  # Latest messages first

Methods:
└── __str__() - Returns "{sender} at {timestamp}"
```

#### NotificationPreference Model
**Location**: `chat/models.py`

```python
NotificationPreference (Table: chat_notificationpreference)
├── id (Primary Key, AutoField)
├── user (OneToOneField → User, on_delete=CASCADE, related_name='notification_preference')
├── enable_sound (BooleanField, default=True)
├── enable_desktop (BooleanField, default=False)
├── enable_email (BooleanField, default=False)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)

Methods:
└── __str__() - Returns "Notification preferences for {user}"
```

### 10.3 URL Patterns

**Location**: `chat/urls.py`

```python
urlpatterns = [
    # Conversation list
    path('conversations/', views.conversation_list, name='conversation_list'),
    
    # Start or view chat with user about product
    path('chat/<int:user_id>/<int:product_id>/', views.chat_detail, name='chat_detail'),
    
    # Send message (POST only)
    path('send_message/<int:conversation_id>/', views.send_message, name='send_message'),
    
    # Get new messages (AJAX)
    path('get_messages/<int:conversation_id>/', views.get_messages, name='get_messages'),
    
    # Get unread count (AJAX)
    path('unread-count/', views.get_unread_count, name='get_unread_count'),
    
    # Notification settings page
    path('notification-settings/', views.notification_settings, name='notification_settings'),
    
    # Get notification preferences (AJAX)
    path('notification-preferences/', views.get_notification_preferences, name='get_notification_preferences'),
]
```

### 10.4 Views and Logic

#### conversation_list View
**Purpose**: Display all user's conversations with unread counts

```python
@login_required
def conversation_list(request):
    """
    Display all conversations for the logged-in user
    Shows unread counts, last message, and product context
    """
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2', 'product').order_by('-updated_at')
    
    # Annotate with last message
    for conv in conversations:
        conv.other_user = conv.get_other_user(request.user)
        conv.unread_count = conv.get_unread_count(request.user)
        conv.last_message = conv.messages.first()  # Due to ordering
    
    return render(request, 'chat/conversation_list.html', {
        'conversations': conversations
    })
```

#### chat_detail View
**Purpose**: Display or create conversation and show messages

```python
@login_required
def chat_detail(request, user_id, product_id):
    """
    Get or create conversation between users about a product
    Mark messages as read for current user
    """
    other_user = get_object_or_404(User, id=user_id)
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create conversation (handles user1/user2 ordering)
    conversation, created = get_or_create_conversation(
        request.user, other_user, product
    )
    
    # Mark as read for current user
    conversation.mark_as_read(request.user)
    
    # Get all messages
    messages = conversation.messages.order_by('timestamp')  # Oldest first for display
    
    return render(request, 'chat/chat_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user,
        'product': product,
    })
```

#### send_message View
**Purpose**: Handle message sending via AJAX

```python
@login_required
@require_POST
def send_message(request, conversation_id):
    """
    Send a message in a conversation
    Increment unread count for other user
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)
    
    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    
    # Increment unread count for other user
    other_user = conversation.get_other_user(request.user)
    if conversation.user1 == other_user:
        conversation.user1_unread_count += 1
    else:
        conversation.user2_unread_count += 1
    conversation.save()
    
    return JsonResponse({
        'id': message.id,
        'content': message.content,
        'sender_id': message.sender.id,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    })
```

#### get_unread_count View
**Purpose**: Return total unread messages for navbar badge

```python
@login_required
def get_unread_count(request):
    """
    Return total unread message count across all conversations
    Used by navbar polling script
    """
    count = Conversation.get_total_unread_count(request.user)
    return JsonResponse({'unread_count': count})
```

#### notification_settings View
**Purpose**: Display and save notification preferences

```python
@login_required
def notification_settings(request):
    """
    Display and update notification preferences
    Creates preference object if doesn't exist
    """
    preference, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        preference.enable_sound = request.POST.get('enable_sound') == 'on'
        preference.enable_desktop = request.POST.get('enable_desktop') == 'on'
        preference.enable_email = request.POST.get('enable_email') == 'on'
        preference.save()
        
        messages.success(request, 'Notification preferences updated!')
        return redirect('chat:notification_settings')
    
    return render(request, 'chat/notification_settings.html', {
        'preference': preference
    })
```

### 10.5 Context Processor

**Location**: `chat/context_processors.py`

```python
def unread_messages(request):
    """
    Add unread message count to all template contexts
    Enables navbar badge to display count globally
    """
    if request.user.is_authenticated:
        from chat.models import Conversation
        count = Conversation.get_total_unread_count(request.user)
        return {'unread_message_count': count}
    return {'unread_message_count': 0}
```

**Configuration**: Added to `settings.py`:
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... other processors
                'chat.context_processors.unread_messages',
            ],
        },
    },
]
```

### 10.6 Frontend Implementation

#### Auto-Polling for New Messages
**Location**: `chat/templates/chat/chat_detail.html`

```javascript
// Poll for new messages every 2 seconds
let lastMessageId = {{ last_message_id|default:0 }};
setInterval(async function() {
    const response = await fetch('{% url "chat:get_messages" conversation.id %}?since=' + lastMessageId);
    const data = await response.json();
    
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
            appendMessage(msg);
            lastMessageId = msg.id;
        });
        scrollToBottom();
    }
}, 2000);
```

#### Unread Badge Polling
**Location**: `theme/templates/base.html`

```javascript
// Update unread count every 15 seconds
setInterval(async function() {
    const response = await fetch('/chat/unread-count/');
    const data = await response.json();
    
    // Update desktop badge
    const badge = document.getElementById('unread-badge');
    if (data.unread_count > 0) {
        badge.textContent = data.unread_count;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
    
    // Update mobile badge
    const mobileBadge = document.querySelector('.mobile-unread-badge');
    if (mobileBadge) {
        if (data.unread_count > 0) {
            mobileBadge.textContent = data.unread_count;
            mobileBadge.classList.remove('hidden');
        } else {
            mobileBadge.classList.add('hidden');
        }
    }
    
    // Update page title
    if (data.unread_count > 0) {
        document.title = `(${data.unread_count}) SRE - Messages`;
    }
}, 15000);
```

### 10.7 UI/UX Design

**Design Principles**:
- Clean light theme matching base template
- White cards on light gray backgrounds
- Minimal shadows and subtle borders
- Indigo accents for branding
- Smooth animations and transitions

**Message Bubbles**:
- Sent messages: Right-aligned, indigo background
- Received messages: Left-aligned, gray background
- Rounded corners with padding
- Timestamps below each message

**Conversation List**:
- Product thumbnail on left
- User avatar with online indicator
- Last message preview
- Unread badge on right
- Hover effects for interactivity

**Mobile Optimization**:
- Touch-friendly tap targets (min 44px)
- Responsive message bubbles
- Mobile menu with Messages icon
- Sticky message input at bottom
- Optimized scrolling behavior

### 10.8 Admin Interface

**Location**: `chat/admin.py`

```python
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user1__email', 'user2__email', 'product__title']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['content', 'sender__email']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'enable_sound', 'enable_desktop', 'enable_email']
    list_filter = ['enable_sound', 'enable_desktop', 'enable_email']
    search_fields = ['user__email']
```

### 10.9 Security Considerations

1. **Authentication**: All chat views require `@login_required` decorator
2. **Authorization**: Users can only access their own conversations
3. **CSRF Protection**: All POST requests include CSRF tokens
4. **XSS Prevention**: Message content escaped in templates
5. **SQL Injection**: Protected by Django ORM parameterization
6. **Privacy**: Conversations private to two participants only

### 10.10 Performance Optimization

1. **Database Queries**:
   - `select_related()` for foreign keys to reduce queries
   - Indexes on frequently queried fields
   - Efficient unread count calculation

2. **Frontend**:
   - Polling intervals balanced for UX vs server load (2s in chat, 15s global)
   - Only fetch new messages since last ID
   - Batch DOM updates for multiple messages

3. **Caching Opportunities** (Future):
   - Cache unread counts with invalidation on new messages
   - Cache conversation lists with TTL
   - Redis for real-time features

### 10.11 Future Enhancements

**Planned Features**:
- WebSocket implementation for true real-time messaging
- Typing indicators
- Message reactions/emojis
- File/image sharing in chat
- Voice/video calling
- Email notification backend implementation
- Push notifications for mobile
- Message search functionality
- Conversation archiving
- Block/report users
- Read receipts with timestamps
- Message editing/deletion

---

## 11. File Structure

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

## 12. Configuration

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

### Media Files Configuration

```python
# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Maximum upload file size (default: 2.5MB in Django)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

**URL Configuration** (`Student_Resource_Exchange/urls.py`):
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your URL patterns ...
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Product Image Upload Path**:
- Images are stored in: `media/products/<seller_id>/<filename>`
- Automatic directory creation per seller
- Up to 5 images per product (image1 to image5)
- Supported formats: JPG, PNG, GIF, WebP
- Automatic filename sanitization

**Important Notes**:
- Media files are served by Django in development (DEBUG=True)
- In production, configure Nginx/Apache to serve media files directly
- Ensure media directory has proper write permissions
- Consider using cloud storage (AWS S3, Cloudinary) for production

---

## 13. Deployment Guide

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

## 14. Troubleshooting

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

## 15. Development Workflow

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

## 16. Recent UI/UX Enhancements (v1.8)

### Chat System Release (v1.8 - October 20, 2025)

**Real-Time Chat Implementation**:
- ✅ Complete messaging system between buyers and sellers
- ✅ Product-context conversations
- ✅ Unread message tracking and badges
- ✅ Auto-polling for real-time updates (2s in chat, 15s globally)
- ✅ Modern light theme UI with message bubbles
- ✅ Mobile-optimized responsive design
- ✅ Notification preferences (sound, desktop, email)
- ✅ Online status indicators
- ✅ Context processor for global unread count

**Technical Implementation**:
- New models: `Conversation`, `Message`, `NotificationPreference`
- AJAX-based polling for real-time feel
- Context processor for navbar badge updates
- Mobile menu enhancement with icon and active states
- Django messages hidden on chat pages to avoid conflicts

**UI/UX Improvements**:
- Clean message bubbles (indigo for sent, gray for received)
- Smooth scrolling and animations
- Pulsing unread badges
- Touch-friendly mobile interface
- Conversation list with product context and last message preview

### Navigation Enhancement (v1.7 - October 19, 2025)

### Global Navigation System

#### Implementation Overview
The navigation system was completely redesigned to provide a consistent, modern experience across all pages.

**Before:** Each page had its own header/navigation implementation, leading to:
- Code duplication across 9+ templates
- Inconsistent styling and behavior
- Maintenance challenges
- No centralized message display

**After:** Single global navbar in `base.html` with:
- DRY (Don't Repeat Yourself) principle
- Consistent branding and behavior
- Alpine.js-powered interactivity
- Centralized message system

#### Key Features

1. **Smart Home Button**
   ```html
   <a href="{% if request.session.user_id %}{% url 'products:product_list' %}{% else %}{% url 'landing:landing' %}{% endif %}">
   ```
   - Logged-in users → Products Marketplace
   - Anonymous users → Landing Page
   - Same logic for logo click

2. **Right-Aligned Navigation**
   ```html
   <div class="hidden md:flex items-center gap-1 ml-auto">
   ```
   - Uses `ml-auto` (margin-left: auto) for modern right alignment
   - Clean, professional look

3. **Context-Aware Menu Items**
   - **Guest Users**: Only "Browse Products" button
   - **Logged-In Users**: Home, Upload Product, Dashboard (admin only)
   - **User Dropdown**: Profile, My Products, Logout

4. **Mobile Responsiveness**
   ```html
   <div x-data="{ mobileMenuOpen: false }">
     <button @click="mobileMenuOpen = !mobileMenuOpen">...</button>
     <div x-show="mobileMenuOpen">...</div>
   </div>
   ```
   - Hamburger menu for mobile devices
   - Slide-in panel with smooth transitions
   - Touch-friendly button sizes

### Pagination System

#### Implementation Details

**View Layer** (`products/views.py`):
```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Paginate with 12 items per page
paginator = Paginator(products, 12)
page = request.GET.get('page', 1)

try:
    products_page = paginator.page(page)
except PageNotAnInteger:
    products_page = paginator.page(1)
except EmptyPage:
    products_page = paginator.page(paginator.num_pages)
```

**Template Layer** (`product_list.html`):
```html
<!-- Page numbers with ellipsis -->
{% for num in products_page.paginator.page_range %}
    {% if num == 1 or num == products_page.paginator.num_pages or num >= products_page.number|add:'-2' and num <= products_page.number|add:'2' %}
        <a href="?page={{ num }}{% if selected_category %}&category={{ selected_category }}{% endif %}{% if search_query %}&search={{ search_query }}{% endif %}">
            {{ num }}
        </a>
    {% elif num == products_page.number|add:'-3' or num == products_page.number|add:'3' %}
        <span>...</span>
    {% endif %}
{% endfor %}
```

**Features:**
- 12 products per page (optimal for grid layouts)
- Smart page range: Shows first, last, current ±2, and ellipsis
- Filter preservation in URLs
- Previous/Next navigation with disabled states
- Page info display: "Showing 1 to 12 of 47 products"

### Global Message System

#### Before (Per-Page Messages)
Each template had its own message display:
- `landing.html`: Floating top-right with animations
- `login.html`: Inline banner style
- `register.html`: Inline banner style
- `profile.html`: Inline banner style
- `dashboard.html`: Inline with close button
- **Problem**: Inconsistent timing, styling, and positioning

#### After (Global Messages)
Single implementation in `base.html`:
```html
{% if messages %}
<div class="fixed top-20 right-4 z-50 space-y-2 max-w-md">
    {% for message in messages %}
    <div x-data="{ show: true }" 
         x-show="show" 
         x-init="setTimeout(() => show = false, 5000)"
         class="animate-fadeInUp ...">
        <!-- Message content -->
    </div>
    {% endfor %}
</div>
{% endif %}
```

**Features:**
- **Position**: `fixed top-20 right-4` (floating top-right corner)
- **Animation**: `fadeInUp` (0.6s ease-out) for smooth entry
- **Auto-dismiss**: 5 seconds using Alpine.js `setTimeout`
- **Color-coded**: Green (success), Red (error), Yellow (warning), Blue (info)
- **Responsive**: Adjusts on mobile devices
- **Consistent**: Same styling across all pages

#### Animation Definition
```css
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

.animate-fadeInUp {
    animation: fadeInUp 0.6s ease-out forwards;
}
```

### Code Cleanup

**Files Modified:**
1. `theme/templates/base.html` - Added global navbar and messages
2. `landing/templates/landing/landing.html` - Removed duplicate header and messages
3. `login/templates/login/login.html` - Removed inline messages
4. `registration/templates/registration/register.html` - Removed inline messages
5. `user_profile/templates/user_profile/profile.html` - Removed inline messages
6. `dashboard/templates/dashboard/dashboard.html` - Removed inline messages
7. `products/views.py` - Added pagination logic
8. `products/templates/products/product_list.html` - Added pagination UI

**Lines of Code Reduced:** ~200+ lines of duplicate HTML removed

### Performance Benefits

1. **Reduced HTML Size**: No duplicate navigation/message code
2. **Faster Load Times**: Single navbar loaded once per session
3. **Better Caching**: Browser can cache base.html effectively
4. **Pagination**: Only 12 products loaded per request instead of all
5. **Alpine.js**: Lightweight (~15KB) for interactive features

### Accessibility Improvements

1. **ARIA Roles**: `role="alert"` on messages, `role="navigation"` on navbar
2. **Keyboard Navigation**: Full keyboard support for dropdowns
3. **Screen Reader Friendly**: Semantic HTML structure
4. **Focus Management**: Proper focus states on interactive elements
5. **Color Contrast**: WCAG AA compliant color combinations

### Browser Compatibility

Tested and working on:
- ✅ Chrome 100+
- ✅ Firefox 95+
- ✅ Safari 15+
- ✅ Edge 100+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

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
