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

### 🎨 Design & UI/UX
- 📱 **Fully Responsive** - Mobile-first design with adaptive layouts
- 🌈 **Modern Light Theme** - Clean white cards on light gray backgrounds with indigo accents
- ✨ **Smooth Animations** - Hover effects, transitions, and auto-dismiss messages
- 💬 **Smart Notifications** - Auto-hide messages after 5 seconds with close buttons
- 🍔 **User Dropdown Menu** - Alpine.js-powered navigation with avatar
- 🎯 **Consistent Branding** - Unified design across all pages
- 🔐 **Login Prompts** - Beautiful gradient CTA boxes for restricted content

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

4. **Install Tailwind CSS dependencies**
   ```bash
   python manage.py tailwind install
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Build Tailwind CSS**
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

10. **Run the development server**
   ```bash
   python manage.py runserver
   ```

11. **Access the application**
   - Landing Page: http://127.0.0.1:8000/
   - Products Marketplace: http://127.0.0.1:8000/products/
   - Registration: http://127.0.0.1:8000/register/
   - Login: http://127.0.0.1:8000/login/
   - User Profile: http://127.0.0.1:8000/profile/ (login required)
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
│   ├── settings.py              # Django settings
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
│   ├── models.py                # Product model (categories, conditions, pricing)
│   ├── views.py                 # Product list & detail views
│   ├── urls.py                  # Product URLs
│   ├── admin.py                 # Django admin configuration
│   ├── templates/               # Product list & detail pages
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
├── theme/                       # Tailwind CSS theme
│   ├── static/                  # Compiled CSS
│   ├── static_src/              # Source files & config
│   └── templates/base.html      # Base template (auto-dismiss messages)
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
├── README.md                    # This file
├── DOCUMENTATION.md             # Detailed technical documentation
└── UI_UX_IMPROVEMENTS.md        # UI/UX changelog
```

## 🛠️ Development

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
2. Browse 10 sample products across different categories
3. Use search and category filters
4. Click on a product to view details
5. Notice seller information is limited (name and college only)
6. See login prompt to view full seller contact details

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
- **Basic Info**: `title`, `description`, `price`
- **Categories**: Books, Notes, Electronics, Stationery, Lab Equipment
- **Condition**: New, Like New, Good, Fair, Poor
- **Images**: Up to 5 images per product (`image1` to `image5`)
  - Automatic upload path: `media/products/<seller_id>/<filename>`
  - Support for primary image and thumbnail gallery
  - Methods: `get_primary_image()`, `get_all_images()`, `has_images()`
- **Status**: `is_available`, `views` (counter)
- **Relationships**: `seller` (ForeignKey to User)
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

- **Amol Solase** - *Initial work* - [GitHub](https://github.com/amol1027/)

## 🙏 Acknowledgments

- Built by students, for students
- Inspired by the need for accessible educational resources
- Thanks to all contributors and testers

## 📞 Support

For support, email support@sre-platform.com or create an issue in the GitHub repository.

## 🗺️ Roadmap

### ✅ Completed (v1.6)
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
- [x] Auto-dismiss messages (5 seconds)
- [x] User dropdown navigation with Alpine.js
- [x] Management command for sample data
- [x] **Product image upload (up to 5 images per product)**
- [x] **Image display with fallback to emoji icons**
- [x] **Product CRUD operations (Create, Read, Update, Delete)**
- [x] **Owner-specific product controls (Edit/Delete buttons)**
- [x] **My Products dashboard with statistics**
- [x] **Thumbnail gallery for multiple product images**
- [x] **Automatic image path management by seller**

### 🚧 In Progress
- [ ] Real-time chat between buyers and sellers
- [ ] Email notifications for new products

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

**Current Version**: 1.6 (Full Product Management)  
**Status**: ✅ Complete product lifecycle with image support  
**Last Updated**: October 19, 2025

### Version History
- **v1.6** (Oct 2025) - Product image upload, CRUD operations, owner controls, My Products dashboard
- **v1.5** (Oct 2025) - Products marketplace, privacy controls, auto-dismiss messages, UI improvements
- **v1.2** (Oct 2025) - Added college/university fields, profile completion tracking
- **v1.0** (Oct 2025) - User authentication, registration, admin dashboard, user profiles
- **v0.5** (Oct 2025) - Landing page and basic structure

## 📖 Documentation

- **[README.md](README.md)** - This file (quick start guide)
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Comprehensive technical documentation
- **[UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md)** - UI/UX changelog and design decisions

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
