# Admin Dashboard

## Overview
The Admin Dashboard provides a comprehensive interface for managing users and monitoring the Student Resource Exchange platform. It features real-time statistics, user management, and detailed analytics.

## Features

### Dashboard Overview (`/dashboard/`)
- **User Statistics**
  - Total users count
  - Verified vs unverified users
  - Recent signups (last 7 days)
  - User ratings distribution
  - Profile completion metrics

- **Quick Actions**
  - View all users
  - Access Django admin
  - Navigate to homepage
  - Add new users

- **Latest Users List**
  - 10 most recent registrations
  - Email verification status
  - Registration dates

### User List (`/dashboard/users/`)
- **Features**:
  - Comprehensive table of all users
  - Search functionality (by email, name, or college ID)
  - Sort by registration date
  - User status indicators
  - Rating display
  - Quick access to details

- **Displayed Information**:
  - User avatar (initial)
  - Name and email
  - College ID
  - Rating (with star icon)
  - Verification status
  - Join date
  - Action buttons

### User Detail (`/dashboard/users/<id>/`)
- **Comprehensive User Profile**:
  - Profile summary card
  - Account status information
  - Contact details
  - Complete address information
  - Profile completion percentage
  - Quick stats

- **Admin Actions**:
  - Edit in Django Admin
  - Navigate back to lists
  - Return to dashboard

## Access Control

### Authentication Required
All dashboard pages require user login:
- Checks for `request.session.user_id`
- Redirects to login page if not authenticated
- Displays error message for unauthorized access

### Session Data
The dashboard uses the following session variables:
- `user_id` - Logged-in user's ID
- `user_email` - User's email address
- `user_name` - User's display name

## URL Structure

| Page | URL | View Function |
|------|-----|---------------|
| Dashboard Home | `/dashboard/` | `dashboard_view` |
| User List | `/dashboard/users/` | `user_list_view` |
| User Detail | `/dashboard/users/<id>/` | `user_detail_view` |

## Statistics Calculated

### User Metrics
```python
total_users = User.objects.count()
verified_users = User.objects.filter(email_verified=True).count()
unverified_users = total_users - verified_users
recent_users = User.objects.filter(created_at__gte=seven_days_ago).count()
```

### Rating Distribution
```python
high_rated = User.objects.filter(rating__gte=4).count()
medium_rated = User.objects.filter(rating__gte=2, rating__lt=4).count()
low_rated = User.objects.filter(rating__lt=2).count()
```

### Address Data
```python
users_with_address = User.objects.filter(
    Q(address_line1__isnull=False) & ~Q(address_line1='')
).count()
```

## Search Functionality

### User List Search
The search feature supports:
- Email addresses
- User names
- College IDs

```python
users = users.filter(
    Q(email__icontains=search_query) |
    Q(name__icontains=search_query) |
    Q(college_id__icontains=search_query)
)
```

## UI/UX Features

### Design Elements
- **Consistent Header**: SRE logo with breadcrumb navigation
- **Responsive Layout**: Mobile-friendly grid system
- **Color-Coded Stats**: 
  - Indigo: Total users
  - Green: Verified users
  - Blue: New users
  - Yellow: Unverified users
  
### Status Badges
- ✅ **Verified**: Green badge
- ⏳ **Pending**: Yellow badge
- ⭐ **Rating**: Star icon with number

### Card Design
- Rounded corners (`rounded-xl`)
- Shadow effects (`shadow-md`)
- Hover animations
- Icon-enhanced stats

## Navigation

### Header Navigation
```
SRE | Dashboard [or] Users [or] Details
                    [Welcome, User!] [Logout]
```

### Quick Access
- Dashboard → User List
- User List → User Details
- User Details → Django Admin
- All pages → Logout

## Integration with Other Apps

### Landing Page
- Shows "Dashboard" link for logged-in users
- Redirects to dashboard after successful login

### Login App
- Redirects to dashboard after login (instead of landing page)
- Session-based authentication

### Registration App
- New users accessible from dashboard
- Statistics updated in real-time

### Django Admin
- Direct links from dashboard
- Edit users in native admin interface

## Usage Examples

### Accessing the Dashboard
1. Log in at `/login/`
2. Automatically redirected to `/dashboard/`
3. View statistics and recent activity

### Searching for a User
1. Go to `/dashboard/users/`
2. Enter search term in search box
3. Click "Search" button
4. Results filtered in real-time

### Viewing User Details
1. From user list, click "View Details"
2. See complete profile information
3. Click "Edit in Django Admin" for modifications

## File Structure

```
dashboard/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── urls.py               # URL routing
├── views.py              # Dashboard views
└── templates/
    └── dashboard/
        ├── dashboard.html      # Main dashboard
        ├── user_list.html      # User list table
        └── user_detail.html    # User profile detail
```

## Screenshots Description

### Dashboard Home
- 4-card stats grid at top
- Quick actions buttons (4 columns)
- 2-column layout:
  - Left: Latest 10 users
  - Right: Statistics charts

### User List
- Search bar at top
- Responsive table with:
  - User avatars (letter initials)
  - Name and email
  - College ID
  - Rating with star
  - Status badges
  - Join date
  - Action links

### User Detail
- 3-column info cards:
  - Profile picture and rating
  - Account status
  - Quick stats
- 2-column detailed info:
  - Contact information
  - Address information
- Action buttons at bottom

## Security Features

1. **Authentication Check**: All views verify user login
2. **Session Validation**: Checks session data integrity
3. **Error Handling**: Graceful fallbacks for missing data
4. **Redirect Protection**: Unauthorized access redirected to login

## Performance Considerations

### Database Queries
- Uses `count()` for efficient counting
- Filters applied at database level
- Limits results with `[:10]` for latest users

### Template Optimization
- Conditional rendering for empty states
- Efficient template inheritance
- Minimal JavaScript dependencies

## Future Enhancements

**Planned Features**:
- [ ] Export users to CSV/Excel
- [ ] Bulk user actions (delete, verify)
- [ ] Advanced filtering options
- [ ] User activity timeline
- [ ] Email verification from dashboard
- [ ] User role management
- [ ] Analytics charts (graphs)
- [ ] Date range filters
- [ ] Pagination for user list
- [ ] User suspension/activation
- [ ] Email notification system
- [ ] Activity logs
- [ ] Real-time notifications

## Troubleshooting

### "Please log in to access the dashboard"
- You're not logged in
- Session has expired
- **Solution**: Go to `/login/` and sign in

### Dashboard shows 0 users
- No users registered yet
- Database is empty
- **Solution**: Register users at `/register/`

### Can't see dashboard link in header
- You're not logged in
- **Solution**: Log in first

### User detail page shows 404
- Invalid user ID
- User was deleted
- **Solution**: Check user exists in admin

---

**App Version**: 1.0  
**Last Updated**: October 17, 2025  
**Part of**: Student Resource Exchange Platform
