# Admin Dashboard Sequence Diagram

## Overview
This sequence diagram shows the admin dashboard workflow, including authentication checks, user statistics, search functionality, and user detail views.

## Sequence Diagram

```mermaid
sequenceDiagram
    actor Admin as Admin User
    participant Decorator as @admin_required
    participant View as Dashboard View
    participant UserModel as User Model
    participant DB as Database

    Note over Admin,DB: Admin Dashboard Flow

    rect rgb(255, 250, 240)
        Note right of Admin: DASHBOARD ACCESS
        
        Admin->>View: GET /dashboard/
        View->>Decorator: Check if user is admin
        
        alt Not Logged In
            Decorator->>Admin: Redirect to /login/
        else Logged In but Not Admin
            Decorator->>Admin: Access denied + Redirect to /profile/
        else Is Admin
            Decorator->>View: Continue
            
            View->>DB: Get user statistics
            Note right of DB: - Total users count<br/>- Verified users count<br/>- Recent users (30 days)
            
            DB-->>View: Statistics data
            
            View->>DB: Get rating distribution
            Note right of DB: Count users by rating<br/>(1-5 stars)
            
            DB-->>View: Rating data
            
            View->>Admin: Render dashboard with analytics
            Note over Admin: Shows:<br/>- User stats cards<br/>- Rating chart<br/>- Recent activity<br/>- Quick actions
        end
    end

    rect rgb(240, 255, 250)
        Note right of Admin: USER SEARCH & LIST
        
        Admin->>View: GET /dashboard/users/?search=query
        
        View->>DB: User.objects.all().order_by('-created_at')
        
        opt Search Query Present
            View->>View: Filter users
            Note right of View: Search in:<br/>- Email<br/>- Name<br/>- College ID
        end
        
        DB-->>View: Filtered user list
        
        View->>Admin: Render user list table
        Note over Admin: Table shows:<br/>- Email, Name<br/>- College, University<br/>- Rating, Verified status<br/>- Join date<br/>- View details link
    end

    rect rgb(250, 240, 255)
        Note right of Admin: USER DETAILS
        
        Admin->>View: GET /dashboard/user/{user_id}/
        
        View->>DB: get_object_or_404(User, id=user_id)
        
        alt User Not Found
            DB-->>View: 404 Not Found
            View->>Admin: Show error page
        else User Found
            DB-->>View: User object
            
            View->>DB: Get user's products
            Note right of DB: Product.objects.filter(<br/>seller=user)
            
            DB-->>View: Product list
            
            View->>Admin: Render user detail page
            Note over Admin: Shows:<br/>- Full profile (14 fields)<br/>- College/University info<br/>- Address details<br/>- Product listings<br/>- Account stats
        end
    end
```

## Flow Description

### Actors and Participants

1. **Admin User** - Authenticated admin accessing dashboard
2. **@admin_required** - Custom decorator enforcing admin access
3. **Dashboard View** - Views handling admin operations
4. **User Model** - Django model for user data
5. **Database** - SQLite database

### Main Flows

**Dashboard Access**
- Admin decorator checks authentication and admin status
- Retrieves statistics: total users, verified users, recent signups
- Calculates rating distribution
- Displays analytics dashboard

**User Search**
- Lists all users with search capability
- Filters by email, name, or college ID
- Shows table with key user information
- Ordered by most recent first

**User Details**
- View complete user profile (all 14 fields)
- See user's product listings
- View verification status and ratings

## Key Features

- **Role-Based Access**: Only admin users allowed
- **Analytics Dashboard**: Real-time user statistics
- **Search Functionality**: Quick user lookup
- **Complete User View**: All profile fields visible
- **Security**: Access control via decorators

## Related Files

- [dashboard/views.py](file:///d:/projects/mini%20project/dashboard/views.py) - Admin views
- [registration/models.py](file:///d:/projects/mini%20project/registration/models.py) - User model
