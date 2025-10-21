# 🎓 Student Resource Exchange (SRE)

A modern web platform built with Django that enables students to share, exchange, and discover educational resources within their community. From textbooks and study notes to tech gadgets, SRE connects students with what they need through a secure marketplace.

![Django](https://img.shields.io/badge/Django-5.1.6-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.x-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🔐 Authentication & User Management
- ✅ **User Registration** - Secure account creation with email, college ID, college name, university name, and address details
- ✅ **Login System** - Session-based authentication with "Remember Me" functionality
- ✅ **Role-Based Access Control** - Separate admin and user permissions
- ✅ **Password Security** - PBKDF2 password hashing with 260,000 iterations
- ✅ **Email Verification Status** - Track verified and unverified users
- ✅ **User Ratings** - 5-star rating system for building trust
- ✅ **Privacy Controls** - Login required to view sensitive seller information

### 🛍️ Products Marketplace
- 📦 **Product Listings** - Browse and search available student resources
- 🔍 **Advanced Search** - Full-text search across product titles and descriptions
- 🏷️ **Category Filters** - Filter by Books, Notes, Electronics, Stationery, Lab Equipment
- 💰 **Pricing & Conditions** - View prices and product condition (New, Like New, Good, Fair, Poor)
- 👁️ **View Counter** - Track product popularity with view counts
- 🔒 **Seller Privacy** - Limited seller info for anonymous users (login required for contact details)
- 📝 **Product Details** - Comprehensive product information with seller ratings
- 🎯 **Related Products** - Discover similar items from the same category
- 📊 **Sample Data** - Pre-loaded with 10 diverse product listings
- 📸 **Image Upload** - Support for up to 5 images per product with automatic path management
- 🖼️ **Image Gallery** - Display actual product images with thumbnail gallery
- ✏️ **Product Management** - Full CRUD operations (Create, Read, Update, Delete)
- 👤 **Owner Controls** - Product owners see Edit/Delete buttons instead of Contact Seller
- 📱 **My Products Dashboard** - View and manage your own product listings with statistics
- 📄 **Smart Pagination** - 12 products per page with page numbers, ellipsis, and navigation
- 🔄 **Filter Preservation** - Category filters and searches preserved across page navigation

### 🔄 Borrow/Lend System (NEW!)
- 🏷️ **Flexible Listing Types** - List items as "For Sale", "For Lending", or "Both"
- 💵 **Smart Pricing** - Set daily rental rates and optional security deposits
- 📅 **Duration Control** - Define maximum borrowing periods for your items
- 📝 **Borrow Requests** - Send requests with desired duration and optional messages
- ✅ **Request Management** - Approve, reject, or cancel borrow requests
- 📊 **Lending Dashboard** - Track pending requests, active loans, and transaction history
- 🔔 **Status Tracking** - Real-time status updates (Pending, Active, Returned, etc.)
- 💬 **Smart Chat Integration** - Direct messaging between borrowers and lenders
- 🔒 **Availability Tracking** - Automatic item locking when borrowed
- 📈 **Transaction History** - Complete record of all lending activities
- 💰 **Cost Calculator** - Real-time calculation of total rental costs
- 🎯 **User-Friendly UI** - Intuitive interfaces for both borrowers and lenders
- ⏰ **Automated Overdue Detection** - Celery background task marks overdue items hourly
- 🔔 **Return Reminders** - Automated reminders sent 2 days before due date

### �👨‍💼 Admin Dashboard
- 📊 **User Statistics** - Real-time metrics for total, verified, and recent users
- 👥 **User Management** - View, search, and manage all registered users
- 🔍 **Advanced Search** - Search users by email, name, or college ID
- 📈 **Analytics** - Rating distribution and profile completion tracking
- 🎯 **User Details** - Comprehensive view including college and university info
- 🔒 **Access Control** - Admin-only access to dashboard features
- 🛒 **Product Management** - Full CRUD operations via Django admin panel

### 👤 User Profile
- 📝 **Personal Profile** - View and manage personal information
- 📍 **Address Management** - Complete address details with multiple fields
- 🎓 **Educational Info** - Display college name and university name
- 📊 **Profile Completion** - Visual circular progress bar tracking 14 fields
- ⭐ **Account Stats** - View rating, verification status, and activity
- 🔄 **Quick Actions** - Easy navigation and profile management

### 💬 Real-Time Chat System
- 🔴 **Live Conversations** - Real-time messaging between buyers and sellers
- 🔔 **Smart Notifications** - Unread message badges in navigation (desktop & mobile)
- 📊 **Conversation Management** - View all conversations with unread counts
- 👤 **User Presence** - Online status indicators for active users
- 🎯 **Product Context** - Chat linked to specific product listings
- 🔕 **Notification Preferences** - Customizable sound, desktop, and email notifications
- 📱 **Mobile Optimized** - Fully responsive chat interface with touch-friendly controls
- 🔄 **Auto-Refresh** - Automatic message polling (2s in chat, 15s for unread counts)
- 🎨 **Modern UI** - Clean light theme with message bubbles and smooth animations
- 📍 **Active States** - Visual indicators for current chat and navigation context

### 🎨 Design & UI/UX
- 📱 **Fully Responsive** - Mobile-first design with adaptive layouts
- 🌈 **Modern Light Theme** - Clean white cards on light gray backgrounds with indigo accents
- ✨ **Smooth Animations** - Hover effects, transitions, fadeInUp animations
- 💬 **Global Message System** - Floating top-right notifications with auto-dismiss (5 seconds)
- 🎯 **Smart Navigation** - Context-aware navbar (logged-in vs guest users)
- 🍔 **User Dropdown Menu** - Alpine.js-powered navigation with avatar
- 🏠 **Smart Home Button** - Routes logged-in users to products, guests to landing page
- 📄 **Pagination** - Clean pagination UI with 12 products per page
- 🎯 **Consistent Branding** - Unified design across all pages with global navbar
- 🔐 **Login Prompts** - Beautiful gradient CTA boxes for restricted content

### ⚙️ Background Tasks & Automation
- 🔄 **Celery Integration** - Asynchronous task processing with Redis
- ⏰ **Scheduled Tasks** - Automated periodic tasks using Celery Beat
- 📊 **Overdue Detection** - Hourly checks for overdue borrowed items
- 🔔 **Smart Reminders** - Daily reminders for upcoming return dates
- 📈 **Task Monitoring** - Database-backed scheduler with admin interface
- 🛡️ **Login Decorators** - Custom decorators for cleaner authentication code
- 🔒 **Permission Decorators** - Role-based access control decorators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for Tailwind CSS)
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/student-resource-exchange.git
   cd student-resource-exchange
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Redis** (Required for Celery)
   ```bash
   # Windows (using WSL)
   wsl -e sudo service redis-server start
   
   # Or using Docker
   docker run -d -p 6379:6379 redis:latest
   
   # Verify Redis is running
   redis-cli ping  # Should return PONG
   ```

5. **Install Tailwind CSS dependencies**
   ```bash
   python manage.py tailwind install
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Build Tailwind CSS**
   ```bash
   python manage.py tailwind build
   ```

8. **Create a superuser (for Django admin access)**
   ```bash
   python manage.py createsuperuser
   ```

9. **Create sample products**
   ```bash
   python manage.py create_sample_products
   ```

10. **Run the development server** (You need 3 terminals)
   
   **Terminal 1 - Django Server:**
   ```bash
   python manage.py runserver
   ```
   
   **Terminal 2 - Celery Worker:**
   ```bash
   celery -A Student_Resource_Exchange worker --loglevel=info --pool=solo
   ```
   
   **Terminal 3 - Celery Beat (Scheduler):**
   ```bash
   celery -A Student_Resource_Exchange beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

11. **Access the application**
   - Landing Page: http://127.0.0.1:8000/
   - Products Marketplace: http://127.0.0.1:8000/products/
   - Registration: http://127.0.0.1:8000/register/
   - Login: http://127.0.0.1:8000/login/
   - User Profile: http://127.0.0.1:8000/profile/ (login required)
   - Chat: http://127.0.0.1:8000/chat/ (login required)
   - My Borrow Requests: http://127.0.0.1:8000/products/my-borrow-requests/ (login required)
   - Lending Dashboard: http://127.0.0.1:8000/products/my-lend-requests/ (login required)
   - Admin Dashboard: http://127.0.0.1:8000/dashboard/ (admin only)
   - Django Admin: http://127.0.0.1:8000/admin/

## 🔑 Admin Access

### Django Admin Panel
Access at `http://127.0.0.1:8000/admin/`

Create a superuser account:
```bash
python manage.py createsuperuser
```

### Custom Admin Dashboard
For admin users who log in through the regular login page:
- Admin users are redirected to `/dashboard/` after login
- Regular users are redirected to `/products/` after login

## 📁 Project Structure

```
mini project/
├── Student_Resource_Exchange/    # Main project settings
│   ├── settings.py              # Django settings (includes Celery config)
│   ├── celery.py                # Celery app configuration
│   ├── __init__.py              # Imports Celery app
│   ├── urls.py                  # Main URL configuration
│   └── wsgi.py                  # WSGI configuration
├── landing/                     # Landing page app
│   ├── templates/               # Hero section & features
│   ├── views.py                 # Landing page logic
│   └── urls.py                  # Landing URLs
├── registration/                # User registration app
│   ├── models.py                # User model with 14 fields (incl. college/university)
│   ├── forms.py                 # Registration form & validation
│   ├── views.py                 # Registration logic
│   ├── templates/               # Registration page
│   └── migrations/              # Database migrations
├── login/                       # Authentication app
│   ├── forms.py                 # Login form
│   ├── views.py                 # Login/logout logic (redirects to products)
│   └── templates/               # Login page
├── products/                    # Products marketplace app
│   ├── models.py                # Product & BorrowRequest models (with borrow/lend fields)
│   ├── views.py                 # Product & borrow/lend management views (with decorators)
│   ├── decorators.py            # Custom decorators (@login_required, @owner_required, etc.)
│   ├── tasks.py                 # Celery background tasks (overdue detection, reminders)
│   ├── forms.py                 # ProductForm & BorrowRequestForm
│   ├── urls.py                  # Product & borrow/lend URLs
│   ├── admin.py                 # Django admin configuration (Product & BorrowRequest)
│   ├── templates/               
│   │   └── products/            
│   │       ├── product_list.html           # Product listing page
│   │       ├── product_detail.html         # Product details with borrow/lend UI
│   │       ├── product_create.html         # Create/List product form
│   │       ├── my_products.html            # User's product dashboard
│   │       ├── borrow_request_create.html  # Borrow request form
│   │       ├── borrow_request_detail.html  # Request details view
│   │       ├── borrow_request_approve.html # Approve request page
│   │       ├── borrow_request_reject.html  # Reject request page
│   │       ├── borrow_request_return.html  # Mark as returned page
│   │       ├── borrow_request_cancel.html  # Cancel request page
│   │       ├── my_borrow_requests.html     # Borrower's requests list
│   │       └── my_lend_requests.html       # Lender's dashboard
│   ├── migrations/              
│   │   └── 0003_*.py            # Borrow/lend feature migration
│   └── management/              
│       └── commands/            
│           └── create_sample_products.py  # Generate 10 sample products
├── dashboard/                   # Admin dashboard app
│   ├── views.py                 # Dashboard, user list, user details
│   ├── templates/               # Dashboard templates
│   ├── templatetags/            # Custom filters (mul, div)
│   └── urls.py                  # Dashboard URLs
├── user_profile/                # User profile app
│   ├── views.py                 # Profile view logic (14-field completion tracking)
│   ├── templates/               # Profile page with circular progress
│   └── urls.py                  # Profile URLs
├── chat/                        # Real-time chat app
│   ├── models.py                # Conversation, Message, NotificationPreference models
│   ├── views.py                 # Chat views, messaging, notification settings
│   ├── urls.py                  # Chat URLs (/conversations/, /chat/<id>/, /settings/)
│   ├── context_processors.py   # Global unread message count for navbar
│   ├── templates/               # Chat UI (conversation list, chat detail, settings)
│   ├── migrations/              # Database migrations (0002_add_notification_preferences)
│   └── admin.py                 # Django admin configuration
├── theme/                       # Tailwind CSS theme
│   ├── static/                  # Compiled CSS
│   ├── static_src/              # Source files & config
│   └── templates/base.html      # Global base template with navbar & messages
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies (includes Celery, Redis)
├── README.md                    # This file
├── DOCUMENTATION.md             # Detailed technical documentation
├── BORROW_LEND_FEATURE.md       # Borrow/lend system documentation
├── CELERY_SETUP.md              # Celery and background tasks guide
├── CELERY_QUICKSTART.md         # Quick reference for Celery setup
└── UI_UX_IMPROVEMENTS.md        # UI/UX changelog
```

## � Documentation

### Quick Reference Guides
- **[CELERY_QUICKSTART.md](CELERY_QUICKSTART.md)** - Quick start guide for Celery and background tasks
- **[QUICK_ACCESS_REFERENCE.md](QUICK_ACCESS_REFERENCE.md)** - Project navigation and quick access guide

### Feature Documentation
- **[BORROW_LEND_FEATURE.md](BORROW_LEND_FEATURE.md)** - Complete borrow/lend system documentation
- **[CHAT_SYSTEM_SUMMARY.md](CHAT_SYSTEM_SUMMARY.md)** - Real-time chat system overview
- **[PRODUCT_UPLOAD_SYSTEM.md](PRODUCT_UPLOAD_SYSTEM.md)** - Product listing and management guide

### Setup & Configuration
- **[CELERY_SETUP.md](CELERY_SETUP.md)** - Comprehensive Celery setup and configuration guide
- **[ADMIN_USER_SETUP.md](ADMIN_USER_SETUP.md)** - Admin user creation and permissions
- **[CHAT_NOTIFICATIONS_GUIDE.md](CHAT_NOTIFICATIONS_GUIDE.md)** - Chat notification setup

### Technical Documentation
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Detailed technical documentation
- **[CHAT_ARCHITECTURE.md](CHAT_ARCHITECTURE.md)** - Chat system architecture
- **[UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md)** - UI/UX changelog and improvements
- **[CHANGELOG.md](CHANGELOG.md)** - Project changelog

## �🛠️ Development

### Running Tailwind in Watch Mode

For automatic CSS rebuilding during development:

```bash
python manage.py tailwind start
```

### Running Tests

```bash
python manage.py test
```

## 🧪 Testing the Application

### Test User Registration
1. Navigate to http://127.0.0.1:8000/register/
2. Fill in all required fields (email, password, college ID, college name, university name)
3. Submit the form
4. Should redirect to login page with success message (auto-dismisses after 5 seconds)

### Test User Login
1. Navigate to http://127.0.0.1:8000/login/
2. Enter registered user credentials
3. Regular users redirect to `/products/` (Products Marketplace)
4. Admin users redirect to `/dashboard/` (Admin Dashboard)

### Test Products Marketplace (Anonymous User)
1. Navigate to http://127.0.0.1:8000/products/
2. Browse products with pagination (12 per page)
3. Use search and category filters
4. Navigate through pages while preserving filters
5. Click on a product to view details
6. Notice seller information is limited (name and college hidden - shows "Verified Seller")
7. See login prompt to view full seller contact details

### Test Products Marketplace (Logged In User)
1. Login first
2. Navigate to products page
3. Click on any product
4. Full seller information visible (email, university, rating)
5. If you're the product owner, you'll see Edit/Delete buttons
6. If you're not the owner, you'll see Contact Seller button

### Test Product Upload
1. Login as a regular user
2. Navigate to http://127.0.0.1:8000/products/create/
3. Fill in product details (title, description, price, category, condition)
4. Upload up to 5 images (optional)
5. Submit the form
6. Should redirect to product detail page with success message

### Test My Products Dashboard
1. Login as a regular user
2. Navigate to http://127.0.0.1:8000/products/my-products/
3. View statistics: Total Products, Available Count, Total Views, Average Price
4. See all your uploaded products in a table
5. Use Edit/Delete actions on your products

### Test Product Editing
1. Login as the product owner
2. View your product detail page
3. Click "Edit Product" button (blue)
4. Update product information and/or images
5. Submit changes
6. Verify updates on product detail page

### Test Product Deletion
1. Login as the product owner
2. View your product detail page or My Products page
3. Click "Delete Product" button (red)
4. Confirm deletion in the popup
5. Product should be removed from database

### Test Owner vs Non-Owner Views
1. **As Owner**: View your own product → See Edit/Delete buttons
2. **As Other User**: View someone else's product → See Contact Seller button
3. **As Anonymous**: View any product → See login prompt for contact details

### Test User Profile
1. Login as a regular user
2. Should redirect to products page
3. Click on user avatar dropdown → "My Profile"
4. View circular progress bar showing profile completion (out of 14 fields)
5. See personal information including college and university

### Test Admin Dashboard
1. Login with admin account
2. Should redirect to `/dashboard/`
3. View user statistics and analytics
4. Search and filter users
5. View user details including college and university info

### Test Real-Time Chat System
1. **Initiate Chat from Product**:
   - Login as User A
   - View any product from User B
   - Click "Contact Seller" button
   - Should redirect to chat with User B about that product

2. **View Conversations**:
   - Navigate to http://127.0.0.1:8000/chat/conversations/
   - See all active conversations with unread counts
   - Notice product context and last message preview
   - Observe online status indicators (green dot for online users)

3. **Send Messages**:
   - Click on a conversation
   - Type message in input box and press Enter or click Send
   - Messages appear instantly with auto-scroll
   - Your messages appear on right (indigo), received on left (gray)

4. **Real-Time Updates**:
   - Open same conversation in two different browsers (different users)
   - Send message from one browser
   - See message appear in other browser within 2 seconds (auto-polling)

5. **Unread Message Badge**:
   - Login and navigate anywhere in the site
   - Notice "Messages" link in navbar shows unread count badge
   - Badge updates automatically every 15 seconds
   - Badge pulses when there are unread messages

6. **Mobile Chat Experience**:
   - Access chat on mobile device or resize browser
   - Mobile menu shows Messages with icon and unread badge
   - Chat interface adapts to mobile screen
   - Touch-friendly message bubbles and input

7. **Notification Settings**:
   - Navigate to http://127.0.0.1:8000/chat/notification-settings/
   - Toggle sound notifications on/off
   - Toggle desktop notifications on/off
   - Toggle email notifications on/off
   - Settings save automatically with success message

8. **Chat Privacy**:
   - Anonymous users cannot access chat
   - Chat requires login - redirects to login page
   - Each conversation linked to specific product

### Test Borrow/Lend System
1. **List Product for Lending**:
   - Login as User A
   - Click "Upload Product"
   - Select "Listing Type" → "For Lending" (or "Sale or Lend")
   - Set "Borrow Price Per Day" (e.g., ₹20)
   - Set "Security Deposit" (e.g., ₹500) - optional
   - Set "Maximum Borrow Days" (e.g., 60)
   - Upload images and complete other fields
   - Submit - Product shows with lending badge and daily rate

2. **Request to Borrow**:
   - Login as User B (different from product owner)
   - Browse products and find a "For Lending" item
   - Click "Request to Borrow" button
   - Enter number of days to borrow
   - Add optional message to lender
   - See real-time cost calculation
   - Submit request

3. **Manage Borrow Requests (Borrower)**:
   - Navigate to "My Borrow Requests" from navigation menu
   - View all your requests with status badges
   - See pending, active, returned, and rejected requests
   - Cancel pending requests if needed
   - Message lenders about active borrows

4. **Lending Dashboard (Lender)**:
   - Navigate to "Lending Dashboard" from navigation menu
   - View statistics: Pending, Active, Completed
   - See pending requests requiring action
   - View borrower details and ratings
   - Read borrower's message

5. **Approve/Reject Requests**:
   - From Lending Dashboard, click "Approve" on a pending request
   - Add optional response message
   - Confirm approval - status changes to "Active"
   - Item marked as currently borrowed (unavailable to others)
   - Or click "Reject" with optional reason

6. **Mark Item as Returned**:
   - When borrower returns the item
   - From Lending Dashboard, find active loan
   - Click "Mark as Returned"
   - Confirm return
   - Item becomes available for lending again
   - Transaction marked as completed

7. **Chat Integration**:
   - From borrow request detail page
   - Click "Message Borrower" (if lender) or "Message Lender" (if borrower)
   - Opens chat with correct person about that specific product
   - Discuss pickup, return, or any issues

8. **View Lending Terms**:
   - Product detail page shows:
     - Listing type badge (For Sale, For Lending, or Both)
     - Daily rental rate
     - Maximum borrow duration
     - Security deposit amount
     - "Request to Borrow" button with cost calculator

### Test Access Control
1. Login as regular user
2. Try accessing http://127.0.0.1:8000/dashboard/
3. Should see "Access denied" and redirect to profile
4. Confirms admin-only access is working

### Test Django Admin Panel
1. Navigate to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Manage Users via registration → Users
4. Manage Products via products → Products
5. Full CRUD operations available

### Collecting Static Files

For production deployment:

```bash
python manage.py collectstatic
```

## 🎨 Design & UI/UX

The platform features a modern, professional design with:
- Responsive layouts for mobile and desktop
- Smooth animations and transitions
- Glass-morphism effects
- Accessible color contrasts
- Optimized touch targets for mobile

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed technical documentation.

## 📚 Technology Stack

### Backend
- **Django 5.1.6** - Python web framework
- **SQLite** - Database (sre1027.sqlite3 for user data)
- **Python 3.13.1** - Programming language
- **PBKDF2** - Password hashing algorithm

### Frontend
- **Tailwind CSS 3.x** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Inter Font** - Modern typography

### Security & Authentication
- **Session-based Auth** - Custom authentication system
- **Role-based Access Control** - Admin/user separation
- **Password Hashing** - 260,000 iterations PBKDF2
- **CSRF Protection** - Django built-in protection

### Development Tools
- **django-tailwind** - Tailwind CSS integration for Django
- **django-browser-reload** - Auto-reload during development

## 🗃️ Database Schema

### User Model (registration app)
The `User` model includes 14 fields:
- **Authentication**: `email` (unique), `password_hash`
- **Profile**: `name`, `college_id`, `college_name`, `university_name`, `rating`
- **Status**: `email_verified`, `is_admin`
- **Address**: 6 fields (`address_line1`, `address_line2`, `city`, `state`, `zip_code`, `country`)
- **Timestamps**: `created_at`, `updated_at`

### Product Model (products app)
The `Product` model includes:
- **Basic Info**: `title`, `description`
- **Categories**: Books, Notes, Electronics, Stationery, Lab Equipment
- **Condition**: New, Like New, Good, Fair, Poor
- **Listing Type**: For Sale, For Lending, or Both
- **Pricing**:
  - `price` - Sale price (nullable for lend-only items)
  - `borrow_price_per_day` - Daily rental rate
  - `borrow_deposit` - Refundable security deposit
  - `max_borrow_days` - Maximum borrowing duration
- **Images**: Up to 5 images per product (`image1` to `image5`)
  - Automatic upload path: `media/products/<seller_id>/<filename>`
  - Support for primary image and thumbnail gallery
  - Methods: `get_primary_image()`, `get_all_images()`, `has_images()`
- **Status**: 
  - `is_available` - Product availability
  - `is_currently_borrowed` - Borrowing status
  - `views` - View counter
- **Relationships**: `seller` (ForeignKey to User)
- **Methods**:
  - `can_be_borrowed()` - Check if available for lending
  - `can_be_purchased()` - Check if available for sale
- **Timestamps**: `created_at`, `updated_at`

### BorrowRequest Model (products app)
The `BorrowRequest` model manages lending transactions:
- **Relationships**:
  - `product` (ForeignKey to Product)
  - `borrower` (ForeignKey to User)
  - `lender` (ForeignKey to User)
- **Request Details**:
  - `requested_days` - Number of days to borrow
  - `status` - Pending, Approved, Active, Returned, Rejected, Cancelled, Overdue
  - `message` - Optional message from borrower
  - `lender_response` - Optional response from lender
- **Financial**:
  - `total_cost` - Calculated rental cost (daily rate × days)
  - `deposit_amount` - Security deposit amount
- **Dates**:
  - `request_date` - When request was created
  - `approved_date` - When lender approved
  - `start_date` - When borrowing started
  - `expected_return_date` - When item should be returned
  - `actual_return_date` - When item was actually returned
- **Methods**:
  - `is_overdue()` - Check if past expected return date
  - `calculate_total_cost()` - Calculate total rental cost
- **Timestamps**: `created_at`, `updated_at`

### Chat Models (chat app)

#### Conversation Model
The `Conversation` model manages chat sessions:
- **Participants**: `user1`, `user2` (ForeignKeys to User)
- **Context**: `product` (ForeignKey to Product) - links chat to specific product
- **Tracking**: `user1_unread_count`, `user2_unread_count` (IntegerFields)
- **Timestamps**: `created_at`, `updated_at`
- **Methods**: 
  - `get_other_user(user)` - Returns the other participant in conversation
  - `get_unread_count(user)` - Returns unread count for specific user
  - `mark_as_read(user)` - Resets unread count for user
  - `get_total_unread_count(user)` (static) - Returns total unread across all conversations

#### Message Model
The `Message` model stores individual chat messages:
- **Relationships**: `conversation` (ForeignKey), `sender` (ForeignKey to User)
- **Content**: `content` (TextField) - the message text
- **Status**: `is_read` (BooleanField, default=False)
- **Timestamps**: `timestamp` (DateTimeField, auto_now_add)
- **Ordering**: Latest messages first (`-timestamp`)

#### NotificationPreference Model
The `NotificationPreference` model stores user notification settings:
- **User**: `user` (OneToOneField to User)
- **Settings**: 
  - `enable_sound` (BooleanField, default=True)
  - `enable_desktop` (BooleanField, default=False)
  - `enable_email` (BooleanField, default=False)
- **Timestamps**: `created_at`, `updated_at`

See [DOCUMENTATION.md](DOCUMENTATION.md) for complete schema details.

## 🚀 Deployment

### Environment Variables

Create a `.env` file in the root directory:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=your-database-url
```

### Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure production database
- [ ] Set up proper `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up static files serving
- [ ] Configure HTTPS
- [ ] Set up logging
- [ ] Configure email backend
- [ ] Run security checks: `python manage.py check --deploy`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Built by students, for students
- Inspired by the need for accessible educational resources
- Thanks to all contributors and testers

## 📞 Support

For support, email support@sre-platform.com or create an issue in the GitHub repository.

## 🗺️ Roadmap

### ✅ Completed (v1.7)
- [x] User authentication and profiles
- [x] User registration with college/university fields
- [x] Login/logout with smart redirects
- [x] Admin dashboard with analytics
- [x] User profile with 14-field completion tracking
- [x] Role-based access control
- [x] Responsive design with light theme
- [x] Session-based authentication
- [x] Password security (PBKDF2)
- [x] User search functionality
- [x] Products marketplace with 5 categories
- [x] Product search and filtering
- [x] Privacy controls for seller information
- [x] Atomic view counter (F() expressions for concurrency safety)
- [x] Related products feature
- [x] Product image upload (up to 5 images per product)
- [x] Image display with fallback to emoji icons
- [x] Product CRUD operations (Create, Read, Update, Delete)
- [x] Owner-specific product controls (Edit/Delete buttons)
- [x] My Products dashboard with statistics
- [x] Thumbnail gallery for multiple product images
- [x] Automatic image path management by seller
- [x] **Global navbar with Alpine.js** - Consistent navigation across all pages
- [x] **Smart Home button** - Routes to products for logged-in users, landing for guests
- [x] **Right-aligned navigation** - Clean, modern navbar layout
- [x] **Simplified guest navigation** - Only "Browse Products" button for non-logged-in users
- [x] **Product pagination** - 12 products per page with smart page controls
- [x] **Filter preservation** - Category and search filters preserved across pagination
- [x] **Global message system** - Floating top-right notifications with fadeInUp animation
- [x] **Auto-dismiss messages** - Messages disappear after 5 seconds automatically
- [x] **Removed duplicate headers** - Single global navbar replaces individual page headers
- [x] **Real-time chat system** - Messaging between buyers and sellers with product context
- [x] **Unread message badges** - Visual indicators in navbar (desktop & mobile)
- [x] **Chat notifications** - Customizable sound, desktop, and email notification preferences
- [x] **Auto-polling updates** - Messages refresh every 2s, unread counts every 15s
- [x] **Modern chat UI** - Light theme with message bubbles and smooth animations
- [x] **Mobile chat optimization** - Touch-friendly interface with responsive design
- [x] **Conversation management** - View all chats with unread counts and online status

### 🚧 In Progress
- [ ] Email notifications backend implementation
- [ ] Typing indicators functionality

### 📋 Planned Features
- [ ] Advanced product filtering (price range, condition, location)
- [ ] Favorites/wishlist functionality
- [ ] User ratings and reviews for transactions
- [ ] Password change and reset feature
- [ ] Email verification workflow
- [ ] Mobile app development
- [ ] Integration with university systems
- [ ] AI-powered product recommendations
- [ ] Multi-language support
- [ ] Transaction history tracking
- [ ] User reputation system
- [ ] Report inappropriate listings

## 📊 Project Status

**Current Version**: 1.9 (Borrow/Lend System)  
**Status**: ✅ Complete borrow/lend marketplace with rental workflows, request management, and lender dashboard  
**Last Updated**: January 2025

### Version History
- **v1.9** (Jan 2025) - Borrow/lend system, rental workflows, deposit management, request tracking, lender dashboard
- **v1.8** (Oct 2025) - Real-time chat system, notification preferences, unread badges, mobile chat optimization
- **v1.7** (Oct 2025) - Global navbar with Alpine.js, smart navigation, pagination (12/page), global message system
- **v1.6** (Oct 2025) - Product image upload, CRUD operations, owner controls, My Products dashboard
- **v1.5** (Oct 2025) - Products marketplace, privacy controls, auto-dismiss messages, UI improvements
- **v1.2** (Oct 2025) - Added college/university fields, profile completion tracking
- **v1.0** (Oct 2025) - User authentication, registration, admin dashboard, user profiles
- **v0.5** (Oct 2025) - Landing page and basic structure

## 📖 Documentation

- **[README.md](README.md)** - This file (quick start guide)
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Comprehensive technical documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md)** - UI/UX changelog and design decisions
- **[ADMIN_USER_SETUP.md](ADMIN_USER_SETUP.md)** - Admin account setup guide
- **[PRODUCT_UPLOAD_SYSTEM.md](PRODUCT_UPLOAD_SYSTEM.md)** - Product upload system documentation
- **[BORROW_LEND_FEATURE.md](BORROW_LEND_FEATURE.md)** - Borrow/Lend system documentation
- **[CHAT_SYSTEM_SUMMARY.md](CHAT_SYSTEM_SUMMARY.md)** - Chat system architecture and features
- **[CHAT_NOTIFICATIONS_GUIDE.md](CHAT_NOTIFICATIONS_GUIDE.md)** - Notification preferences guide
- **[REALTIME_CHAT_GUIDE.md](REALTIME_CHAT_GUIDE.md)** - Real-time chat implementation details
- **[QUICK_ACCESS_REFERENCE.md](QUICK_ACCESS_REFERENCE.md)** - Quick reference guide

## 🎯 User Roles

### Admin Users
- Access to admin dashboard at `/dashboard/`
- View all users and statistics
- Search and filter users
- View detailed user information including college/university
- Manage platform analytics
- Full access to Django admin panel at `/admin/`
- Manage products and users

### Regular Users
- Login redirects to products marketplace at `/products/`
- Access to personal profile at `/profile/`
- View and browse all products
- Search and filter products by category
- View full seller contact information (when logged in)
- Profile completion tracking (14 fields)
- Account statistics and ratings
- **Upload products** - Create new product listings at `/products/create/`
- **Manage products** - View all your products at `/products/my-products/`
- **Edit products** - Modify your own product listings
- **Delete products** - Remove your product listings with confirmation
- **Upload images** - Add up to 5 images per product
- **Owner controls** - See Edit/Delete buttons on your own products instead of Contact Seller
- **Chat with sellers** - Initiate conversations from product pages
- **Manage conversations** - View all chats at `/chat/conversations/`
- **Real-time messaging** - Send and receive messages with auto-refresh
- **Notification settings** - Customize chat notification preferences at `/chat/notification-settings/`
- **Unread tracking** - See unread message counts in navbar

### Anonymous Users (Not Logged In)
- Browse products marketplace
- View limited product information
- See seller name and college only
- Prompted to login for full seller contact details
- Cannot contact sellers directly

## 🔒 Security Features

- ✅ PBKDF2 password hashing with 260,000 iterations
- ✅ Session-based authentication
- ✅ Role-based access control (RBAC)
- ✅ CSRF protection on all forms
- ✅ Password strength validation (min 8 characters)
- ✅ Email uniqueness validation
- ✅ Secure session management
- ✅ Admin-only dashboard access
- ✅ Privacy controls for seller information
- ✅ Login-required access to sensitive data
- ✅ XSS protection via Django templates
- ✅ SQL injection protection via Django ORM
- ✅ **Atomic database operations** - View counter uses F() expressions to prevent race conditions

## 🚀 Performance & Concurrency

### Atomic View Counter
The product view counter is implemented using Django's `F()` expressions to ensure **concurrency safety**:

```python
# Atomic increment - prevents race conditions
Product.objects.filter(pk=product.pk).update(views=F('views') + 1)
```

**Benefits**:
- ✅ **Thread-safe**: Multiple simultaneous requests won't cause lost updates
- ✅ **Race condition free**: No read-modify-write cycle that could lose concurrent increments
- ✅ **Database-level guarantee**: Operation is atomic at the database level
- ✅ **Performance**: Single UPDATE query instead of SELECT + UPDATE
- ✅ **Accurate counting**: All views are correctly tracked even under high traffic

**How it works**: The increment happens directly in the database with SQL like:
```sql
UPDATE products_product SET views = views + 1 WHERE id = <product_id>;
```

This ensures that even if 100 users view a product simultaneously, all 100 increments are correctly counted.

## 🚀 Management Commands

### Create Sample Products
Generate 10 diverse product listings for testing:
```bash
python manage.py create_sample_products
```

Creates products across all categories (books, notes, electronics, stationery, lab equipment) with realistic descriptions, pricing, and conditions.

### Create Superuser
Create an admin account for Django admin panel:
```bash
python manage.py createsuperuser
```

### Database Migrations
Apply database schema changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

**Made with ❤️ by Amol Solase**
