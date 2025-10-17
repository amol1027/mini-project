# Login App

## Overview
The login app handles user authentication for the Student Resource Exchange platform. It validates user credentials, manages sessions, and provides a secure login/logout system.

## Features

### User Login
- **URL**: `http://localhost:8000/login/`
- Email-based authentication
- Password verification using hashed passwords
- "Remember me" functionality
- Session management

### User Logout
- **URL**: `http://localhost:8000/login/logout/`
- Clears user session
- Redirects to landing page

## Form Fields

### Login Form
- **Email Address** (required)
  - Type: email
  - Validation: Email format
  
- **Password** (required)
  - Type: password
  - Validation: Required field
  
- **Remember Me** (optional)
  - Type: checkbox
  - Sets session expiry (2 weeks if checked, browser close if unchecked)

## Authentication Flow

1. User enters email and password
2. System validates form data
3. System looks up user by email
4. System verifies password using `check_password()` method
5. If valid:
   - Creates user session
   - Stores user info in session (user_id, user_email, user_name)
   - Sets session expiry based on "Remember me"
   - Redirects to landing page
   - Shows success message
6. If invalid:
   - Shows error message
   - Form redisplayed with values

## Session Management

### Session Data Stored
- `user_id` - User's primary key
- `user_email` - User's email address
- `user_name` - User's display name

### Session Expiry
- **Remember Me Checked**: 2 weeks (1,209,600 seconds)
- **Remember Me Unchecked**: Browser close (session expires when browser is closed)

## Security Features

1. **Password Verification**
   - Uses Django's `check_password()` function
   - Compares against hashed password in database
   - Never exposes plain text passwords

2. **CSRF Protection**
   - All forms include CSRF tokens
   - Protects against cross-site request forgery

3. **Session Security**
   - Secure session management
   - Automatic session cleanup on logout

4. **Error Messages**
   - Generic error messages to prevent user enumeration
   - "Invalid email or password" for both incorrect email and password

## UI Features

### Login Page Design
- Consistent with landing and registration pages
- Clean, modern card design
- Gradient background decorations
- Responsive layout (mobile-friendly)
- Header with navigation
- Back to home link
- Sign up link for new users

### Form Features
- Auto-focus on email field
- Clear error messages
- Success feedback
- Placeholder text
- Required field indicators (*)
- Remember me checkbox
- Forgot password link (placeholder)

## Usage

### Accessing the Login Page
Navigate to: `http://localhost:8000/login/`

### Testing Login
1. Register a new user first at `/register/`
2. Go to `/login/`
3. Enter your registered email and password
4. Click "Sign In"
5. You'll be redirected to the landing page
6. Header will show "Welcome, [Your Name]!" and a Logout button

### Logging Out
1. Click "Log out" button in the header
2. Session is cleared
3. Redirected to landing page
4. Success message displayed

## Integration with Other Apps

### Landing Page
- Shows login button when user is not logged in
- Shows welcome message and logout button when logged in
- Conditional rendering based on session data

### Registration Page
- Link to login page for existing users
- Consistent UI styling

## File Structure

```
login/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py              # LoginForm
├── models.py
├── tests.py
├── urls.py               # URL routing
├── views.py              # login_view, logout_view
└── templates/
    └── login/
        └── login.html    # Login page template
```

## Code Examples

### Checking if User is Logged In (in templates)
```django
{% if request.session.user_id %}
    <!-- User is logged in -->
    <p>Welcome, {{ request.session.user_name }}!</p>
{% else %}
    <!-- User is not logged in -->
    <a href="{% url 'login:login' %}">Log in</a>
{% endif %}
```

### Checking if User is Logged In (in views)
```python
def my_view(request):
    if request.session.get('user_id'):
        # User is logged in
        user_id = request.session['user_id']
        user_email = request.session['user_email']
        # ... do something
    else:
        # User is not logged in
        return redirect('login:login')
```

### Protecting Views (Require Login)
```python
from django.shortcuts import redirect

def protected_view(request):
    # Check if user is logged in
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # User is logged in, proceed with view
    # ...
```

## Error Handling

### Form Validation Errors
- Invalid email format
- Empty required fields
- Display inline with field

### Authentication Errors
- User not found
- Incorrect password
- Display as: "Invalid email or password"

### Session Errors
- Session timeout
- Invalid session data
- Automatically handled by Django

## Testing

### Manual Testing Checklist
- [ ] Access login page
- [ ] Submit empty form (should show errors)
- [ ] Submit with non-existent email (should show error)
- [ ] Submit with wrong password (should show error)
- [ ] Submit with correct credentials (should login successfully)
- [ ] Test "Remember me" functionality
- [ ] Test logout functionality
- [ ] Verify session persistence across page loads
- [ ] Test responsive design on mobile
- [ ] Verify navigation links work correctly

## Future Enhancements

**Planned Features**:
- [ ] Password reset functionality
- [ ] Email verification before login
- [ ] Two-factor authentication (2FA)
- [ ] Social login (Google, GitHub, etc.)
- [ ] Login attempt limiting (brute force protection)
- [ ] Password strength requirements
- [ ] Account lockout after failed attempts
- [ ] Login history tracking
- [ ] Device management
- [ ] Session management (view active sessions)

## Troubleshooting

### "Invalid email or password" Error
- Verify user exists in database
- Check password was set correctly during registration
- Try registering a new user

### Session Not Persisting
- Check browser cookies are enabled
- Verify SESSION_ENGINE in settings.py
- Clear browser cache and cookies

### Redirect Loop
- Check for conflicting redirects in views
- Verify URL patterns are correct
- Check middleware order

---

**App Version**: 1.0  
**Last Updated**: October 17, 2025  
**Part of**: Student Resource Exchange Platform
