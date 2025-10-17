# Registration App

## Overview
The registration app handles user registration for the Student Resource Exchange platform. It provides a complete user registration system with form validation and database storage.

## Features

### User Registration Form
The registration form collects the following information:
- **Email Address** (required, unique)
- **Password** (required, minimum 8 characters)
- **Confirm Password** (required, must match password)
- **College ID** (required)
- **Full Name** (optional)
- **Address Information** (all optional):
  - Address Line 1
  - Address Line 2
  - City
  - State/Province
  - ZIP/Postal Code
  - Country

### Database Structure
**Database Name:** `sre1027.sqlite3`

**Table Name:** `user`

**Fields:**
- `id` - Primary key, auto-generated
- `email` - Email address (unique, indexed)
- `password_hash` - Hashed password
- `college_id` - College identification number
- `name` - Full name (optional)
- `rating` - User rating (default: 0)
- `email_verified` - Email verification status (default: False)
- `address_line1` - First line of address (optional)
- `address_line2` - Second line of address (optional)
- `city` - City (optional)
- `state_province` - State or province (optional)
- `zip_postal_code` - ZIP or postal code (optional)
- `country` - Country (optional)
- `created_at` - Timestamp of account creation (auto-generated)
- `updated_at` - Timestamp of last update (auto-updated)

## URL Structure
- Registration page: `http://localhost:8000/register/`

## Form Validation
The registration form includes the following validations:
1. **Email Validation**
   - Must be a valid email format
   - Must be unique (not already registered)

2. **Password Validation**
   - Minimum 8 characters
   - Must match the confirm password field

3. **Required Fields**
   - Email, Password, Confirm Password, and College ID are required
   - All address fields are optional

## Security Features
- Passwords are hashed using Django's built-in password hashing (PBKDF2)
- CSRF protection enabled
- Email uniqueness enforced at database level

## Usage

### Accessing the Registration Page
Navigate to: `http://localhost:8000/register/`

### Running the Development Server
```powershell
cd "d:\projects\mini project"
python manage.py runserver
```

### Admin Interface
The User model is registered in the Django admin panel:
- Access: `http://localhost:8000/admin/`
- View and manage registered users
- Organized fieldsets for better user experience

## Files Structure
```
registration/
├── __init__.py
├── admin.py          # Admin configuration
├── apps.py
├── forms.py          # Registration form
├── models.py         # User model
├── urls.py           # URL routing
├── views.py          # Registration view
├── migrations/
│   └── 0001_initial.py
└── templates/
    └── registration/
        └── register.html  # Registration template
```

## Next Steps (Future Enhancements)
1. Add email verification functionality
2. Implement login/logout functionality
3. Add password reset feature
4. Add user profile editing
5. Implement user rating system
6. Add profile picture upload
7. Create user dashboard
