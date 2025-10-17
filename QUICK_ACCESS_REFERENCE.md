# Quick Reference: Admin & User Access

## 🔑 Admin Credentials
```
Email:    amolsolse2127@gmail.com
Password: amolsolse2127@gmail.com
```

## 🌐 Important URLs

| URL | Access | Description |
|-----|--------|-------------|
| `/login/` | Everyone | Single login page for all users |
| `/register/` | Guest only | User registration (NOT for admins) |
| `/dashboard/` | **Admin only** | Admin dashboard with user management |
| `/profile/` | **Regular users** | User profile page |
| `/` | Everyone | Landing page |

## 🚪 Login Behavior

### Admin Login
1. Go to `/login/`
2. Enter admin credentials
3. → Redirected to `/dashboard/`
4. Navigation shows: **"Dashboard"** link

### Regular User Login
1. Go to `/login/`
2. Enter user credentials
3. → Redirected to `/profile/`
4. Navigation shows: **"Profile"** link

## 🛡️ Access Control

### Dashboard Pages
- ✅ Admin: Full access
- ❌ Regular Users: "Access denied" → Redirected to `/profile/`
- ❌ Guests: "Please log in" → Redirected to `/login/`

### Profile Page
- ✅ Regular Users: Can view their own profile
- ✅ Admin: Can view their own profile (but usually use dashboard)
- ❌ Guests: "Please log in" → Redirected to `/login/`

## 📊 User Types

| Type | is_admin | Can Register | Access |
|------|----------|--------------|--------|
| **Admin** | `True` | ❌ No | Dashboard, Profile |
| **User** | `False` | ✅ Yes | Profile only |

## 🔧 Creating New Admins

### Option 1: Script
```bash
python create_admin.py
# Edit the email/password in the script first
```

### Option 2: Django Shell
```bash
python manage.py shell
```
```python
from registration.models import User

# Make existing user admin
user = User.objects.get(email='email@example.com')
user.is_admin = True
user.save()

# Or create new admin
admin = User(
    email='admin@example.com',
    college_id='ADMIN002',
    name='Admin Name',
    email_verified=True,
    is_admin=True
)
admin.set_password('secure_password')
admin.save()
```

## 🎯 Features by Role

### Admin Dashboard
- View all users
- Search users
- User statistics
- User details
- Platform analytics
- User ratings breakdown
- Verification status tracking

### User Profile
- Personal information
- Address details
- Profile completion %
- Account statistics
- Member since date
- Rating display
- Email verification status

## 📱 Navigation

### When Logged In as Admin:
```
Header: Products | Features | About | Dashboard | Welcome, Admin! | Logout
```

### When Logged In as User:
```
Header: Products | Features | About | Profile | Welcome, User! | Logout
```

### When Not Logged In:
```
Header: Products | Features | About | Log in →
```

## ⚠️ Important

1. **NO separate admin login button** - Single login form for everyone
2. **NO admin registration** - Admins created manually only
3. **Automatic redirect** - System detects user type on login
4. **Session-based** - Role stored in session (`is_admin`)
5. **Protected routes** - Dashboard checks admin status on every request

## 🧪 Test Scenarios

### Test 1: Admin Access
```
✓ Login as admin → Goes to /dashboard/
✓ Can view user list
✓ Can view user details
✓ Navigation shows "Dashboard"
```

### Test 2: User Access
```
✓ Register new user
✓ Login → Goes to /profile/
✓ Cannot access /dashboard/ (redirected with error)
✓ Navigation shows "Profile"
```

### Test 3: Guest Access
```
✓ Try /dashboard/ → Redirected to login
✓ Try /profile/ → Redirected to login
✓ Can access / (landing page)
✓ Can access /login/ and /register/
```

---

**Last Updated**: October 17, 2025
