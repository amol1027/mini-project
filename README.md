# 🎓 Student Resource Exchange (SRE)

A modern web platform built with Django that enables students to share, exchange, and discover educational resources within their community. From textbooks and study notes to tech gadgets, SRE connects students with what they need.

![Django](https://img.shields.io/badge/Django-5.1.6-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.x-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### � Authentication & User Management
- ✅ **User Registration** - Secure account creation with email, college ID, and address details
- ✅ **Login System** - Session-based authentication with "Remember Me" functionality
- ✅ **Role-Based Access Control** - Separate admin and user permissions
- ✅ **Password Security** - PBKDF2 password hashing with 260,000 iterations
- ✅ **Email Verification Status** - Track verified and unverified users
- ✅ **User Ratings** - 5-star rating system for building trust

### 👨‍💼 Admin Dashboard
- 📊 **User Statistics** - Real-time metrics for total, verified, and recent users
- 👥 **User Management** - View, search, and manage all registered users
- � **Advanced Search** - Search users by email, name, or college ID
- 📈 **Analytics** - Rating distribution and profile completion tracking
- 🎯 **User Details** - Comprehensive view of individual user profiles
- 🔒 **Access Control** - Admin-only access to dashboard features

### 👤 User Profile
- 📝 **Personal Profile** - View and manage personal information
- 📍 **Address Management** - Complete address details with multiple fields
- � **Profile Completion** - Visual progress tracking for profile setup
- ⭐ **Account Stats** - View rating, verification status, and activity
- 🔄 **Quick Actions** - Easy navigation and profile management

### 🎨 Design & UI/UX
- 📱 **Fully Responsive** - Mobile-first design with adaptive layouts
- 🌈 **Modern Gradient UI** - Beautiful purple-indigo gradient themes
- ✨ **Smooth Animations** - Hover effects and transitions throughout
- 🍔 **Mobile Menu** - Slide-in navigation with Alpine.js
- 🎯 **Consistent Branding** - Unified design across all pages

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

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Registration: http://127.0.0.1:8000/register/
   - Login: http://127.0.0.1:8000/login/
   - Admin Dashboard: http://127.0.0.1:8000/dashboard/ (admin only)
   - User Profile: http://127.0.0.1:8000/profile/ (regular users)
   - Django Admin: http://127.0.0.1:8000/admin/

## 🔑 Default Admin Credentials

For admin dashboard access:
```
Email:    amolsolse2127@gmail.com
Password: amolsolse2127@gmail.com
```

> ⚠️ **Important**: Change these credentials in production!

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
│   ├── models.py                # User model with 14+ fields
│   ├── forms.py                 # Registration form & validation
│   ├── views.py                 # Registration logic
│   ├── templates/               # Registration page
│   └── migrations/              # Database migrations
├── login/                       # Authentication app
│   ├── forms.py                 # Login form
│   ├── views.py                 # Login/logout logic
│   └── templates/               # Login page
├── dashboard/                   # Admin dashboard app
│   ├── views.py                 # Dashboard, user list, user details
│   ├── templates/               # Dashboard templates
│   ├── templatetags/            # Custom filters (mul, div)
│   └── urls.py                  # Dashboard URLs
├── user_profile/                # User profile app
│   ├── views.py                 # Profile view logic
│   ├── templates/               # Profile page
│   └── urls.py                  # Profile URLs
├── theme/                       # Tailwind CSS theme
│   ├── static/                  # Compiled CSS
│   ├── static_src/              # Source files & config
│   └── templates/base.html      # Base template
├── db.sqlite3                   # Django admin database
├── sre1027.sqlite3             # User data database
├── manage.py                    # Django management script
├── README.md                    # This file
├── DOCUMENTATION.md             # Detailed documentation
├── ADMIN_USER_SETUP.md          # Admin setup guide
└── QUICK_ACCESS_REFERENCE.md    # Quick reference guide
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
2. Fill in all required fields
3. Submit the form
4. Should redirect to login page with success message

### Test User Login
1. Navigate to http://127.0.0.1:8000/login/
2. Enter registered user credentials
3. Should redirect to `/profile/` (user profile page)

### Test Admin Login
1. Navigate to http://127.0.0.1:8000/login/
2. Enter admin credentials:
   - Email: `amolsolse2127@gmail.com`
   - Password: `amolsolse2127@gmail.com`
3. Should redirect to `/dashboard/` (admin dashboard)

### Test Access Control
1. Login as regular user
2. Try accessing http://127.0.0.1:8000/dashboard/
3. Should see "Access denied" and redirect to profile
4. Confirms admin-only access is working

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

### User Model
The `User` model includes:
- **Authentication**: `email`, `password_hash`
- **Profile**: `name`, `college_id`, `rating`
- **Status**: `email_verified`, `is_admin`
- **Address**: 6 fields (line1, line2, city, state, zip, country)
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

### ✅ Completed (v1.0)
- [x] User authentication and profiles
- [x] User registration with validation
- [x] Login/logout system
- [x] Admin dashboard with analytics
- [x] User profile management
- [x] Role-based access control
- [x] Responsive design
- [x] Session-based authentication
- [x] Password security (PBKDF2)
- [x] User search functionality

### 🚧 In Progress
- [ ] Profile editing functionality
- [ ] Password change feature
- [ ] Email verification workflow

### 📋 Planned Features
- [ ] Resource posting and management
- [ ] Advanced search and filtering
- [ ] Real-time chat between users
- [ ] Mobile app development
- [ ] Integration with university systems
- [ ] AI-powered resource recommendations
- [ ] Multi-language support
- [ ] Email notification system
- [ ] User suspension/activation
- [ ] Activity logs and analytics

## 📊 Project Status

**Current Version**: 1.0 (Authentication & User Management)  
**Status**: ✅ Core features completed  
**Last Updated**: October 17, 2025

### Version History
- **v1.0** (Oct 2025) - User authentication, registration, admin dashboard, user profiles
- **v0.5** (Oct 2025) - Landing page and basic structure

## 📖 Documentation

- **[README.md](README.md)** - This file (quick start guide)
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Comprehensive technical documentation
- **[ADMIN_USER_SETUP.md](ADMIN_USER_SETUP.md)** - Admin and user access control guide
- **[QUICK_ACCESS_REFERENCE.md](QUICK_ACCESS_REFERENCE.md)** - Quick reference for credentials and URLs

## 🎯 User Roles

### Admin Users
- Access to admin dashboard at `/dashboard/`
- View all users and statistics
- Search and filter users
- View detailed user information
- Manage platform analytics

### Regular Users
- Access to personal profile at `/profile/`
- View and manage own information
- Profile completion tracking
- Account statistics

## 🔒 Security Features

- ✅ PBKDF2 password hashing with 260,000 iterations
- ✅ Session-based authentication
- ✅ Role-based access control (RBAC)
- ✅ CSRF protection on all forms
- ✅ Password strength validation (min 8 characters)
- ✅ Email uniqueness validation
- ✅ Secure session management
- ✅ Admin-only dashboard access

---

**Made with ❤️ by Amol Solase**
