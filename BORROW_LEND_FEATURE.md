# Borrow/Lend Feature Documentation

## Overview
The Borrow/Lend feature allows users to not only sell items but also lend them out for a specified duration. This creates a sharing economy within the Student Resource Exchange platform where students can temporarily borrow items they need without having to purchase them.

## Key Features

### 1. **Flexible Listing Types**
Products can be listed as:
- **For Sale** - Traditional selling
- **For Lending** - Only available for borrowing
- **Both** - Available for either purchase or borrowing

### 2. **Borrow Request System**
- Students can send borrow requests for items
- Specify desired duration (in days)
- Add optional message to lender
- Real-time cost calculation

### 3. **Lending Terms**
- **Daily Rental Rate**: Set price per day
- **Security Deposit**: Optional refundable deposit
- **Maximum Duration**: Set maximum borrowing period
- **Availability Tracking**: Items marked as borrowed are unavailable to others

### 4. **Request Management**
Lenders can:
- View all pending requests
- Approve or reject requests with optional messages
- Track active loans
- Mark items as returned

Borrowers can:
- Track all their borrow requests
- Cancel pending requests
- View expected return dates
- Communicate with lenders

### 5. **Status Tracking**
Request statuses:
- **Pending** - Awaiting lender approval
- **Approved** - Accepted but not yet collected
- **Active** - Item currently borrowed
- **Returned** - Item returned successfully
- **Rejected** - Request declined by lender
- **Cancelled** - Cancelled by borrower
- **Overdue** - Past expected return date

## Database Schema

### Product Model Additions
```python
listing_type = CharField  # 'sell', 'lend', or 'both'
price = DecimalField  # Sale price (nullable for lend-only items)
borrow_price_per_day = DecimalField  # Daily rental rate
borrow_deposit = DecimalField  # Security deposit amount
max_borrow_days = IntegerField  # Maximum lending duration
is_currently_borrowed = BooleanField  # Availability flag
```

### BorrowRequest Model
```python
product = ForeignKey(Product)
borrower = ForeignKey(User)
lender = ForeignKey(User)
requested_days = IntegerField
status = CharField  # pending, approved, active, returned, etc.
message = TextField  # Borrower's message
total_cost = DecimalField  # Calculated rental cost
deposit_amount = DecimalField
request_date = DateTimeField
approved_date = DateTimeField
start_date = DateField
expected_return_date = DateField
actual_return_date = DateField
lender_response = TextField
```

## URL Routes

### Borrow/Lend Management
- `/products/<id>/borrow/` - Create borrow request
- `/products/borrow-requests/<id>/` - View request details
- `/products/borrow-requests/<id>/approve/` - Approve request
- `/products/borrow-requests/<id>/reject/` - Reject request
- `/products/borrow-requests/<id>/return/` - Mark as returned
- `/products/borrow-requests/<id>/cancel/` - Cancel request
- `/products/my-borrow-requests/` - View all borrow requests (borrower)
- `/products/my-lend-requests/` - Lending dashboard (lender)

## User Workflows

### Creating a Lendable Listing
1. Navigate to "Upload Product"
2. Select listing type: "For Lending" or "Both"
3. Set daily rental rate
4. (Optional) Set security deposit
5. Set maximum borrow duration
6. Upload images and complete other details
7. Submit listing

### Borrowing an Item
1. Browse products and find item with "For Lending" badge
2. Click "Request to Borrow"
3. Enter desired number of days
4. Add optional message to lender
5. Review total cost calculation
6. Submit request
7. Wait for lender approval
8. Communicate details via chat
9. Collect item and use
10. Return item to lender

### Managing Lending Requests (Lender)
1. Check "Lending Dashboard" from navigation
2. View dashboard with stats:
   - Pending requests
   - Active loans
   - Completed transactions
3. For pending requests:
   - Review borrower details and rating
   - Read borrower's message
   - Approve or reject with optional message
4. For active loans:
   - Track expected return dates
   - Mark as returned when item comes back
5. View transaction history

## Navigation Updates

### Desktop Menu (User Dropdown)
- My Profile
- My Products
- **My Borrow Requests** ← NEW
- **Lending Dashboard** ← NEW
- Messages
- Logout

### Mobile Menu
- Home
- Upload Product
- My Profile
- My Products
- **My Borrow Requests** ← NEW
- **Lending Dashboard** ← NEW
- Messages
- Admin Dashboard (if admin)
- Logout

## Product Detail Page Updates

The product detail page now dynamically displays:

1. **Listing Type Badge** - Shows whether item is for sale, lending, or both
2. **Purchase Button** - For items available for sale
3. **Borrow Button** - For items available for lending
4. **Lending Terms Card** - Shows:
   - Daily rental rate
   - Maximum duration
   - Security deposit (if any)
5. **Message Seller** - Always available for inquiries

## Forms

### ProductForm Enhancements
New fields:
- `listing_type` - Dropdown selection
- `borrow_price_per_day` - Daily rental rate
- `borrow_deposit` - Security deposit
- `max_borrow_days` - Maximum duration

Validation:
- Sale price required for "sell" or "both" types
- Borrow price required for "lend" or "both" types

### BorrowRequestForm
Fields:
- `requested_days` - Number of days to borrow
- `message` - Optional message to lender

Features:
- Real-time cost calculation
- Maximum days validation
- Dynamic help text

## Admin Interface

Both models are registered in Django admin:

### Product Admin
- List display includes listing_type and is_currently_borrowed
- Filters by listing_type
- Organized fieldsets for pricing and lending terms

### BorrowRequest Admin
- List display shows all key information
- Filters by status and dates
- Readonly fields for timestamps
- Organized fieldsets for easy management

## Business Logic

### Product Availability
- Products marked as `is_currently_borrowed=True` cannot be borrowed again
- Sale purchases are not affected by borrow status
- When item is returned, `is_currently_borrowed` is set back to False

### Cost Calculation
```python
total_cost = borrow_price_per_day × requested_days
total_payment = total_cost + deposit_amount
refund_amount = deposit_amount (upon return)
```

### Date Management
- `start_date` set when request is approved
- `expected_return_date` calculated: start_date + requested_days
- `actual_return_date` set when lender marks as returned
- Overdue detection: current_date > expected_return_date

## Security & Validation

1. **Authentication Required** - All borrow/lend actions require login
2. **Owner Checks** - Users cannot borrow their own items
3. **Duplicate Prevention** - Cannot create multiple pending/active requests for same item
4. **Status Validation** - Operations only allowed in appropriate states
5. **Permission Checks** - Only lenders can approve/reject/mark returned

## Future Enhancements (Possible)

1. **Payment Integration** - Actual payment processing
2. **Rating System** - Rate borrowers and lenders after transactions
3. **Deposit Management** - Automated deposit hold and refund
4. **Reminders** - Email/notification reminders for return dates
5. **Late Fees** - Automatic calculation of late return fees
6. **Insurance Options** - Optional insurance for high-value items
7. **Calendar Integration** - View item availability calendar
8. **Wishlist** - Save items to borrow later
9. **Reviews** - Leave reviews for borrowed items
10. **Analytics** - Earnings dashboard for lenders

## Technical Implementation

### Files Modified/Created

#### Models
- `products/models.py` - Added fields to Product, created BorrowRequest model

#### Views  
- `products/views.py` - Added 8 new views for borrow/lend management

#### Forms
- `products/forms.py` - Updated ProductForm, added BorrowRequestForm

#### Templates
- `products/templates/products/product_detail.html` - Enhanced with borrow UI
- `products/templates/products/borrow_request_create.html` - NEW
- `products/templates/products/borrow_request_detail.html` - Would be created
- `products/templates/products/borrow_request_approve.html` - NEW
- `products/templates/products/borrow_request_reject.html` - NEW
- `products/templates/products/borrow_request_return.html` - NEW
- `products/templates/products/borrow_request_cancel.html` - NEW
- `products/templates/products/my_borrow_requests.html` - NEW
- `products/templates/products/my_lend_requests.html` - NEW
- `theme/templates/base.html` - Updated navigation

#### URLs
- `products/urls.py` - Added 8 new URL patterns

#### Admin
- `products/admin.py` - Registered BorrowRequest model

#### Migrations
- `products/migrations/0003_*.py` - Database schema changes

## Usage Examples

### Example 1: Listing a Textbook for Lending
```
Title: Data Structures & Algorithms Textbook
Category: Books
Condition: Good
Listing Type: For Lending
Daily Rate: ₹20
Deposit: ₹500
Max Duration: 60 days
```

### Example 2: Calculator for Both Sale and Lending
```
Title: Scientific Calculator TI-84
Category: Electronics
Condition: Like New
Listing Type: Sale or Lend
Sale Price: ₹2,500
Daily Rental: ₹30
Deposit: ₹1,000
Max Duration: 30 days
```

### Example 3: Lab Equipment for Semester-long Lending
```
Title: Arduino Starter Kit
Category: Lab Equipment
Condition: Good
Listing Type: For Lending
Daily Rate: ₹15
Deposit: ₹2,000
Max Duration: 120 days
```

## Support & Troubleshooting

### Common Issues

**Q: Why can't I borrow my own item?**
A: The system prevents self-borrowing to avoid conflicts and maintain clear transaction records.

**Q: What happens if someone doesn't return my item?**
A: Use the chat system to communicate. In future versions, we'll add dispute resolution.

**Q: Can I edit borrow terms after listing?**
A: Yes, use the "Edit Product" button, but this won't affect existing active loans.

**Q: How do I handle damaged returns?**
A: Discuss with borrower via chat. The deposit system is designed to cover such cases.

**Q: Can I have multiple active loans of the same item?**
A: No, each item can only be borrowed by one person at a time.

---

## Installation & Setup

The feature is fully integrated. After pulling the code:

```bash
# Apply migrations
python manage.py migrate products

# The feature is ready to use!
```

## Testing Checklist

- [ ] Create product with "For Lending" type
- [ ] Create product with "Both" type  
- [ ] Send borrow request
- [ ] Approve borrow request
- [ ] Reject borrow request
- [ ] Cancel pending request
- [ ] Mark item as returned
- [ ] View borrow requests list
- [ ] View lending dashboard
- [ ] Check navigation links work
- [ ] Test cost calculator
- [ ] Verify product becomes unavailable when borrowed
- [ ] Verify product becomes available after return

---

**Version**: 1.0
**Last Updated**: October 20, 2025
**Author**: Student Resource Exchange Development Team
