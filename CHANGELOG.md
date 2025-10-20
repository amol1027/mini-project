# Changelog

All notable changes to the Student Resource Exchange project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2025-10-19

### Added
- **Global Navigation System**
  - Unified navbar in `base.html` used across all pages
  - Smart Home button that routes logged-in users to products, guests to landing page
  - Right-aligned navigation menu with `ml-auto` for modern layout
  - Alpine.js-powered user dropdown menu with avatar and initials
  - Responsive mobile hamburger menu with slide-in panel
  - Context-aware navigation items (different for guests vs logged-in users)
  
- **Product Pagination**
  - 12 products per page for optimal performance
  - Smart page navigation with Previous/Next buttons
  - Page numbers with ellipsis for large page counts (e.g., 1 ... 5 6 7 ... 20)
  - Filter preservation across pages (category and search queries persist in URLs)
  - Page info display: "Showing X to Y of Z products"
  - Error handling for invalid page numbers
  
- **Global Message System**
  - Floating top-right notifications (`fixed top-20 right-4 z-50`)
  - FadeInUp animation (0.6s ease-out) for smooth entry
  - Auto-dismiss after 5 seconds using Alpine.js
  - Color-coded messages: Green (success), Red (error), Yellow (warning), Blue (info)
  - SVG icons for each message type
  - Consistent styling across all pages

### Changed
- **Navigation Simplification**
  - Guest users now only see "Browse Products" button in navbar
  - Removed "My Products" from main navbar (kept only in user dropdown)
  - Logo click now uses smart navigation (products for logged-in, landing for guests)
  
- **Privacy Enhancements**
  - Seller name and college information completely hidden for non-logged-in users
  - Generic "Verified Seller" placeholder with icon displayed instead
  - Login prompt to view seller contact details

### Removed
- **Code Cleanup**
  - Removed duplicate headers from 9+ template files:
    - `landing/templates/landing/landing.html`
    - `login/templates/login/login.html`
    - `registration/templates/registration/register.html`
    - `user_profile/templates/user_profile/profile.html`
    - `dashboard/templates/dashboard/dashboard.html`
    - `products/templates/products/product_list.html`
    - `products/templates/products/product_detail.html`
    - `dashboard/templates/dashboard/user_list.html`
    - `dashboard/templates/dashboard/user_detail.html`
  - Removed duplicate message display code from individual templates
  - Reduced codebase by ~200+ lines of duplicate HTML

### Fixed
- Message display timing now consistent across all pages
- Navigation state properly maintained across page transitions
- Pagination preserves search and filter parameters in URLs

### Technical Details
- Updated `products/views.py` to use Django Paginator (12 items/page)
- Added `EmptyPage` and `PageNotAnInteger` exception handling
- Implemented Alpine.js `x-data`, `x-show`, `x-init` for auto-dismiss messages
- Uses Tailwind utility classes for responsive design

---

## [1.6.0] - 2025-10-19

### Added
- **Product Image Upload System**
  - Support for up to 5 images per product
  - Automatic upload path management: `media/products/<seller_id>/<filename>`
  - Primary image display with thumbnail gallery
  - Fallback to emoji icons when no images available
  
- **Full Product CRUD Operations**
  - Create: Upload new products with images at `/products/create/`
  - Read: Browse and view detailed product information
  - Update: Edit product details and images at `/products/<id>/edit/`
  - Delete: Remove products with confirmation modal
  
- **Owner-Specific Controls**
  - Product owners see Edit/Delete buttons on their listings
  - Non-owners see Contact Seller button instead
  - `is_owner` boolean passed to templates for conditional rendering
  
- **My Products Dashboard**
  - New route: `/products/my-products/`
  - Statistics: Total Products, Available Count, Total Views, Average Price
  - Table view of all seller's products with Edit/Delete actions
  - Quick navigation to product details

### Technical Details
- Added Product model methods: `get_primary_image()`, `get_all_images()`, `has_images()`
- Image upload uses Django `models.ImageField` with dynamic upload paths
- Owner detection using session comparison: `product.seller.id == request.session['user_id']`

---

## [1.5.0] - 2025-10-18

### Added
- **Products Marketplace**
  - Browse products with search and category filters
  - Product detail pages with seller information
  - View counter using Django F() expressions for concurrency safety
  - Related products feature (same category)
  
- **Privacy Controls**
  - Limited seller information for anonymous users
  - Login required to view seller contact details
  - "Login to view details" prompts with gradient CTAs
  
- **Auto-Dismiss Messages**
  - Messages automatically hide after 5 seconds
  - Smooth fade-out animations
  
- **User Dropdown Navigation**
  - Alpine.js-powered dropdown menu
  - User avatar with initials
  - Quick links to Profile, My Products, Logout

### Changed
- Improved UI with modern light theme
- Enhanced hover effects and transitions
- Better mobile responsiveness

---

## [1.2.0] - 2025-10-17

### Added
- **College and University Fields**
  - Added `college_name` to User model
  - Added `university_name` to User model
  - Updated registration form with new fields
  
- **Profile Completion Tracking**
  - Circular progress bar showing completion out of 14 fields
  - Visual representation of profile completeness
  - Field count display

### Changed
- User profile page now displays college and university information
- Admin dashboard shows college and university in user details
- Updated registration flow to collect educational information

---

## [1.0.0] - 2025-10-15

### Added
- **User Authentication System**
  - Session-based authentication
  - PBKDF2 password hashing with 260,000 iterations
  - Login/Logout functionality
  - Smart redirects (admin → dashboard, user → products)
  
- **User Registration**
  - Comprehensive registration form with 14 fields
  - Email uniqueness validation
  - Password strength requirements (min 8 characters)
  - Address information collection (6 fields)
  - Email verification status tracking
  
- **Admin Dashboard**
  - User statistics (total, verified, recent)
  - User management (view, search, filter)
  - Rating distribution analytics
  - Profile completion tracking
  - User details view with college/university info
  
- **User Profile**
  - Personal information display
  - Address management
  - Educational information (college, university)
  - Account statistics (rating, verification)
  - Profile completion progress
  
- **Role-Based Access Control**
  - Admin-only dashboard access
  - User-specific redirects
  - Access denied messages for unauthorized access

### Security
- CSRF protection on all forms
- XSS protection via Django templates
- SQL injection protection via Django ORM
- Secure session management
- Password hashing with PBKDF2

---

## [0.5.0] - 2025-10-14

### Added
- **Landing Page**
  - Hero section with CTA buttons
  - Features showcase (6 cards)
  - About section
  - Call-to-action section
  - Responsive footer
  
- **Tailwind CSS Integration**
  - django-tailwind package
  - Custom theme configuration
  - Utility-first CSS approach
  - DaisyUI component library
  
- **Alpine.js Integration**
  - Lightweight JavaScript framework
  - Interactive components
  - Mobile menu functionality

### Technical Infrastructure
- Django 5.1.6 project setup
- SQLite database configuration
- Static files management
- Template structure
- URL routing

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

**For detailed technical documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)**  
**For quick start guide, see [README.md](README.md)**
