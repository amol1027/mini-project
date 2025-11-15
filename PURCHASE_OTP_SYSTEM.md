# Purchase OTP System Documentation

## Overview
The Purchase OTP system implements an Uber-style OTP verification for buy/sell transactions, similar to the existing borrow/lend OTP system. This ensures secure handover of purchased items between buyer and seller.

## Database Models

### PurchaseRequest Model
Located in `products/models.py`

**Purpose**: Tracks buy/sell requests and transactions

**Key Fields**:
- `product`: ForeignKey to Product
- `buyer`: User making the purchase
- `seller`: User selling the item
- `status`: pending, approved, completed, rejected, cancelled
- `purchase_price`: Agreed sale price
- `message`: Buyer's message to seller
- `seller_response`: Seller's response message
- `handover_otp_verified`: Boolean flag for OTP verification
- `handover_otp_verified_at`: Timestamp of verification
- `request_date`, `approved_date`, `completed_date`: Transaction timeline

**Status Flow**:
```
pending → approved → completed
  ↓         ↓
rejected  cancelled
```

### PurchaseOTP Model
Located in `products/models.py`

**Purpose**: Manages OTP codes for purchase handover verification

**Key Fields**:
- `purchase_request`: ForeignKey to PurchaseRequest
- `otp_code`: 6-digit numeric code
- `is_verified`: Verification status
- `verified_at`: Verification timestamp
- `verified_by`: User who verified the OTP
- `expires_at`: OTP expiry time (15 minutes default)
- `attempts`: Number of verification attempts
- `max_attempts`: Maximum allowed attempts (5 default)

**Methods**:
- `is_expired()`: Check if OTP has expired
- `is_valid()`: Check if OTP can still be verified
- `verify(user, entered_otp)`: Verify the OTP code

## OTP Utility Functions

### Core Functions (in `products/otp_utils.py`)

#### `create_purchase_handover_otp(purchase_request)`
Creates a handover OTP when seller approves purchase request.
- Generates 6-digit numeric OTP
- Sets 15-minute expiry
- Reuses active OTP if exists

#### `get_active_purchase_otp(purchase_request)`
Retrieves the current active (unverified, not expired) OTP for a purchase.

#### `verify_purchase_otp(purchase_request, user, entered_otp)`
Verifies the handover OTP.
- Checks OTP validity
- Updates PurchaseRequest status to 'completed'
- Marks product as unavailable (sold)
- Returns (success, message, otp)

#### `send_purchase_otp_notification(purchase_request, notification_type='handover')`
Sends OTP notifications via chat system.
- Creates/retrieves conversation between buyer and seller
- Sends OTP to buyer (who gives it to seller)
- Sends notification to seller
- Uses recipient field for targeted visibility

## How It Works

### Purchase Flow

1. **Buyer Initiates Purchase**
   - Buyer sends purchase request for a product
   - Status: `pending`

2. **Seller Approves Request**
   - Seller reviews and approves the request
   - Status: `pending → approved`
   - Handover OTP is generated automatically
   - OTP sent to buyer via chat

3. **Item Handover**
   - Buyer and seller meet for item transfer
   - Buyer shares the OTP with seller
   - Seller enters OTP in purchase dashboard
   - System verifies OTP

4. **Transaction Complete**
   - On successful verification:
     - Status: `approved → completed`
     - Product marked as unavailable/sold
     - Transaction timestamp recorded
     - `handover_otp_verified` = True

### OTP Message Flow

**To Buyer** (recipient=buyer):
```
🎉 PURCHASE APPROVED!

Your purchase of '[Product Title]' has been approved by the seller.

📱 HANDOVER OTP: 123 456

Give this OTP to the seller during item handover to complete the purchase.
The seller will verify this OTP to confirm you've received the item.

⏰ Valid for 15 minutes
```

**To Seller** (recipient=seller):
```
📊 PURCHASE APPROVED - OTP GENERATED

You approved [Buyer Name]'s purchase request for '[Product Title]'.

The buyer has been sent a handover OTP. During item transfer,
ask the buyer for the OTP and verify it in the purchase dashboard
to complete the transaction.

💰 Sale Price: ₹[Amount]
```

## Security Features

1. **Time-Limited**: OTP expires in 15 minutes
2. **Attempt Limits**: Maximum 5 verification attempts
3. **Single-Use**: OTP can only be verified once
4. **Targeted Visibility**: Only intended recipient sees OTP message
5. **Atomic Transactions**: Database updates wrapped in transactions

## Comparison with Borrow OTP System

| Feature | Borrow/Lend | Buy/Sell |
|---------|-------------|----------|
| OTP Types | Acceptance + Return | Handover only |
| Participants | Borrower + Lender | Buyer + Seller |
| OTP Holder | Borrower | Buyer |
| Verifier | Lender | Seller |
| Item Status After | Currently borrowed / Returned | Sold (unavailable) |
| Reversible | Yes (can return) | No (permanent sale) |

## Admin Interface

Both `PurchaseRequest` and `PurchaseOTP` are registered in Django admin:
- View all purchase requests and their status
- Monitor OTP generation and verification
- Track transaction timeline
- Search by product, buyer, seller

## Integration Points

### Chat System
- Uses existing `Conversation` and `Message` models
- Leverages `recipient` field for OTP visibility
- System messages with type `'otp_handover'`

### Product Status
- Automatically marks product as unavailable after sale
- Prevents duplicate purchases
- Updates `is_available` flag

## Future Enhancements

1. **Payment Integration**: Link with payment gateway
2. **Ratings & Reviews**: Buyer rates seller after purchase
3. **Dispute Resolution**: Handle failed transactions
4. **OTP Resend**: Allow regenerating expired OTPs
5. **SMS/Email Notifications**: Multi-channel OTP delivery
6. **Purchase History**: Comprehensive transaction logs

## Migration

Migration file: `products/migrations/0008_purchaseotp_purchaserequest_and_more.py`

Run migrations:
```bash
python manage.py migrate products
```

## Testing Checklist

- [ ] Create purchase request
- [ ] Approve request (OTP generated)
- [ ] Verify OTP messages appear in chat
- [ ] Test OTP verification (correct code)
- [ ] Test OTP verification (wrong code)
- [ ] Test OTP expiry (after 15 min)
- [ ] Test maximum attempts limit
- [ ] Verify product marked unavailable
- [ ] Check admin interface
- [ ] Test with multiple purchase requests

## Files Modified/Created

**Created**:
- `PURCHASE_OTP_SYSTEM.md` (this file)

**Modified**:
- `products/models.py`: Added PurchaseRequest and PurchaseOTP models
- `products/otp_utils.py`: Added purchase OTP functions
- `products/admin.py`: Registered new models
- `products/migrations/0008_*.py`: Database migration

## Related Documentation

- `OTP_SYSTEM_DOCUMENTATION.md`: Original borrow/lend OTP system
- `CELERY_IMPLEMENTATION_SUMMARY.md`: Background task processing
- `chat/README.md`: Chat system integration
