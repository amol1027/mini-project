# User Login Sequence Diagram

## Overview
This sequence diagram shows the user authentication workflow in the Student Resource Exchange application, including password verification, session management, and role-based routing.

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User as User (Browser)
    participant View as Login View
    participant Form as Login Form
    participant Model as User Model
    participant Session as Session Manager
    participant DB as Database

    Note over User,DB: User Login Flow

    User->>View: GET /login/
    
    alt User Already Logged In
        View->>Session: Check session['user_id']
        Session-->>View: User ID exists
        View->>View: Check session['is_admin']
        
        alt Is Admin
            View->>User: Redirect to /dashboard/
        else Regular User
            View->>User: Redirect to /products/
        end
    else User Not Logged In
        View->>Form: Create empty LoginForm()
        View->>User: Render login page with form
    end

    User->>View: POST /login/ (email, password, remember_me)
    View->>Form: LoginForm(request.POST)
    
    Form->>Form: Validate form fields
    Note right of Form: - Email format<br/>- Required fields
    
    alt Form Invalid
        Form-->>View: Return validation errors
        View->>User: Show error message
    else Form Valid
        Form-->>View: cleaned_data
        
        View->>DB: User.objects.get(email=email)
        
        alt User Not Found
            DB-->>View: DoesNotExist exception
            View->>User: Error: "Invalid email or password"
        else User Found
            DB-->>View: User object
            View->>Model: check_password(password)
            
            Note right of Model: Verify password hash<br/>using PBKDF2
            
            alt Password Invalid
                Model-->>View: False
                View->>User: Error: "Invalid email or password"
            else Password Valid
                Model-->>View: True
                
                View->>Session: Set session data
                Note right of Session: - user_id<br/>- user_email<br/>- user_name<br/>- is_admin
                
                alt Remember Me Checked
                    View->>Session: set_expiry(1209600)
                    Note right of Session: 2 weeks (14 days)
                else Remember Me Unchecked
                    View->>Session: set_expiry(0)
                    Note right of Session: Until browser close
                end
                
                View->>User: Success message
                Note over User: "Welcome back, [name]!"
                
                alt Is Admin User
                    View->>User: Redirect to /dashboard/
                else Regular User
                    View->>User: Redirect to /products/
                end
            end
        end
    end
```

## Flow Description

### Actors and Participants

1. **User (Browser)** - The student logging into the application
2. **Login View** - Django view handling authentication (`login/views.py`)
3. **Login Form** - Django form validating credentials (`login/forms.py`)
4. **User Model** - Django model with password verification methods
5. **Session Manager** - Django session framework for state management
6. **Database** - SQLite database storing user records

### Main Flow Steps

1. **Initial Request (GET)**
   - User navigates to `/login/`
   - View checks if user already authenticated
   - If logged in, redirects based on role (admin → dashboard, user → products)
   - If not logged in, shows login form

2. **Credential Submission (POST)**
   - User enters email, password, and optionally checks "Remember Me"
   - Browser sends POST request with credentials

3. **Form Validation**
   - Form validates email format and required fields
   - If invalid, shows errors
   - If valid, proceeds to authentication

4. **User Lookup**
   - View queries database for user by email
   - If not found, shows generic error message (security: don't reveal if email exists)
   - If found, proceeds to password verification

5. **Password Verification**
   - User model's `check_password()` method verifies hash
   - Uses PBKDF2 algorithm with 260,000 iterations
   - Compares submitted password against stored hash

6. **Session Management**
   - On successful authentication, session data stored:
     - `user_id` - Unique user identifier
     - `user_email` - User's email address
     - `user_name` - Display name
     - `is_admin` - Admin privilege flag
   - Session expiry set based on "Remember Me" option:
     - **Checked**: 2 weeks (1,209,600 seconds)
     - **Unchecked**: Browser session (expires on close)

7. **Role-Based Redirect**
   - Admin users → `/dashboard/` (Admin Dashboard)
   - Regular users → `/products/` (Products Marketplace)

## Key Features

- **Session-Based Authentication**: Uses Django's session framework (no tokens/JWT)
- **Password Security**: PBKDF2 hashing with 260,000 iterations
- **Role-Based Access**: Separate routes for admin and regular users
- **Remember Me**: Optional extended session duration
- **Security**: Generic error messages don't reveal if email exists
- **Already Logged In Check**: Prevents re-login and redirects appropriately

## Related Files

- [login/views.py](file:///d:/projects/mini%20project/login/views.py) - Login and logout logic
- [login/forms.py](file:///d:/projects/mini%20project/login/forms.py) - Login form validation
- [registration/models.py](file:///d:/projects/mini%20project/registration/models.py) - User model with `check_password()` method
