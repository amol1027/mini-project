"""
OTP Utility Functions for Borrow/Lend System
Uber-style OTP verification for item acceptance and return
"""

import random
import string
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db import transaction
from .models import BorrowOTP


def generate_otp(length=6):
    """
    Generate a random numeric OTP code
    
    Args:
        length (int): Length of OTP code (default 6)
    
    Returns:
        str: Random numeric OTP code
    """
    return ''.join(random.choices(string.digits, k=length))


def create_acceptance_otp(borrow_request):
    """
    Create an acceptance OTP for when borrower picks up the item
    Similar to Uber's pickup OTP
    
    Args:
        borrow_request: BorrowRequest instance
    
    Returns:
        BorrowOTP: Created OTP instance
    """
    from .models import BorrowOTP
    
    # If there's an active (unverified & not expired) acceptance OTP, reuse it
    from .models import BorrowOTP as _BorrowOTP
    active = get_active_otp(borrow_request, 'acceptance')
    if active:
        return active

    # Otherwise generate and persist a new OTP
    otp_code = generate_otp()
    otp = BorrowOTP.objects.create(
        borrow_request=borrow_request,
        otp_type='acceptance',
        otp_code=otp_code,
        expires_at=timezone.now() + timedelta(minutes=15)
    )
    
    # Cache OTP for quick lookup
    cache_key = f'acceptance_otp_{borrow_request.id}'
    cache.set(cache_key, otp_code, timeout=900)  # 15 minutes
    
    return otp


def create_return_otp(borrow_request):
    """
    Create a return OTP for when borrower returns the item
    Similar to Uber's drop-off OTP
    
    Args:
        borrow_request: BorrowRequest instance
    
    Returns:
        BorrowOTP: Created OTP instance
    """
    from .models import BorrowOTP
    
    # If there's an active (unverified & not expired) return OTP, reuse it
    active = get_active_otp(borrow_request, 'return')
    if active:
        return active

    # Otherwise generate and persist a new OTP
    otp_code = generate_otp()
    otp = BorrowOTP.objects.create(
        borrow_request=borrow_request,
        otp_type='return',
        otp_code=otp_code,
        expires_at=timezone.now() + timedelta(minutes=15)
    )
    
    # Cache OTP for quick lookup
    cache_key = f'return_otp_{borrow_request.id}'
    cache.set(cache_key, otp_code, timeout=900)  # 15 minutes
    
    return otp


def verify_otp(borrow_request, otp_type, entered_otp, user):
    """
    Verify an OTP code
    
    Args:
        borrow_request: BorrowRequest instance
        otp_type (str): 'acceptance' or 'return'
        entered_otp (str): OTP code entered by user
        user: User instance who is verifying
    
    Returns:
        tuple: (success: bool, message: str, otp: BorrowOTP or None)
    """
    from .models import BorrowOTP
    
    # Get the latest unverified OTP of this type
    try:
        otp = BorrowOTP.objects.filter(
            borrow_request=borrow_request,
            otp_type=otp_type,
            is_verified=False
        ).latest('created_at')
    except BorrowOTP.DoesNotExist:
        return False, "No active OTP found. Please request a new OTP.", None
    
    # Verify the OTP
    success, message = otp.verify(user, entered_otp)
    
    # Clear cache on successful verification
    if success:
        cache_key = f'{otp_type}_otp_{borrow_request.id}'
        cache.delete(cache_key)
    
    return success, message, otp if success else None


def get_active_otp(borrow_request, otp_type):
    """
    Get the active (unverified, non-expired) OTP for a borrow request
    
    Args:
        borrow_request: BorrowRequest instance
        otp_type (str): 'acceptance' or 'return'
    
    Returns:
        BorrowOTP or None: Active OTP if exists
    """
    from .models import BorrowOTP
    
    try:
        otp = BorrowOTP.objects.filter(
            borrow_request=borrow_request,
            otp_type=otp_type,
            is_verified=False
        ).latest('created_at')
        
        # Check if still valid
        if otp.is_valid():
            return otp
        return None
    except BorrowOTP.DoesNotExist:
        return None


def resend_otp(borrow_request, otp_type):
    """
    Resend/Regenerate OTP (useful if user didn't receive or OTP expired)
    
    Args:
        borrow_request: BorrowRequest instance
        otp_type (str): 'acceptance' or 'return'
    
    Returns:
        BorrowOTP: New OTP instance
    """
    # Force regeneration: delete any existing unverified OTPs of this type
    BorrowOTP.objects.filter(
        borrow_request=borrow_request,
        otp_type=otp_type,
        is_verified=False
    ).delete()

    if otp_type == 'acceptance':
        return create_acceptance_otp(borrow_request)
    elif otp_type == 'return':
        return create_return_otp(borrow_request)
    else:
        raise ValueError(f"Invalid OTP type: {otp_type}")


def send_otp_notification(borrow_request, otp, recipient_type='borrower'):
    """
    Send OTP notification to user (via chat/message system)
    In a real application, this could send SMS or email
    
    Args:
        borrow_request: BorrowRequest instance
        otp: BorrowOTP instance
        recipient_type (str): 'borrower' or 'lender'
    
    Returns:
        bool: Success status
    """
    from chat.models import Conversation, Message
    
    try:
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            buyer=borrow_request.borrower,
            seller=borrow_request.lender,
            product=borrow_request.product
        )
        
        # Determine recipient and message
        if otp.otp_type == 'acceptance':
            # Acceptance phase: Send OTP to BORROWER (they show it to lender)
            sender = borrow_request.lender
            
            # Message to borrower with OTP
            message_to_borrower = (
                f"✅ BORROW REQUEST APPROVED!\n\n"
                f"🔑 YOUR PICKUP OTP: {otp.otp_code}\n\n"
                f"📍 INSTRUCTIONS:\n"
                f"1. Show this OTP to {borrow_request.lender.name} when picking up the item\n"
                f"2. The lender will enter this OTP to confirm handover\n"
                f"3. This OTP expires in 15 minutes\n\n"
                f"📦 Item: {borrow_request.product.title}\n"
                f"💰 Total Cost: ₹{borrow_request.total_cost}\n"
                f"📅 Duration: {borrow_request.requested_days} days"
            )
            
            # Create a system message intended specifically for the borrower
            Message.objects.create(
                conversation=conversation,
                # Sender is the lender (origin of the approval), recipient is the borrower
                sender=borrow_request.lender,
                recipient=borrow_request.borrower,
                content=message_to_borrower,
                is_read=False,
                is_system_message=True,
                message_type='otp_handover'
            )
            
            # Also notify lender
            message_to_lender = (
                f"� REQUEST APPROVED - OTP GENERATED\n\n"
                f"The borrower ({borrow_request.borrower.name}) will show you a 6-digit OTP when picking up the item.\n\n"
                f"⚠️ IMPORTANT: Only hand over the item AFTER verifying their OTP!\n\n"
                f"📦 Item: {borrow_request.product.title}\n"
                f"⏰ OTP expires in 15 minutes"
            )
            
            # Create a system message intended specifically for the lender
            Message.objects.create(
                conversation=conversation,
                # Sender is the borrower (informing lender), recipient is the lender
                sender=borrow_request.borrower,
                recipient=borrow_request.lender,
                content=message_to_lender,
                is_read=False,
                is_system_message=True,
                message_type='otp_handover'
            )
            
        else:  # return OTP
            # Return phase: Send OTP to BORROWER (they show it to lender)
            sender = borrow_request.borrower
            
            # Message to borrower with return OTP
            message_to_borrower = (
                f"🔙 RETURN OTP GENERATED!\n\n"
                f"� YOUR RETURN OTP: {otp.otp_code}\n\n"
                f"📍 INSTRUCTIONS:\n"
                f"1. Show this OTP to {borrow_request.lender.name} when returning the item\n"
                f"2. The lender will enter this OTP to confirm return\n"
                f"3. This OTP expires in 15 minutes\n\n"
                f"📦 Item: {borrow_request.product.title}\n"
                f"✨ Thank you for using our platform responsibly!"
            )
            
            # Create a system message intended specifically for the borrower
            Message.objects.create(
                conversation=conversation,
                # Sender is borrower, recipient is borrower (system notice to borrower)
                sender=borrow_request.borrower,
                recipient=borrow_request.borrower,
                content=message_to_borrower,
                is_read=False,
                is_system_message=True,
                message_type='otp_return'
            )
            
            # Also notify lender about incoming return
            message_to_lender = (
                f"📬 RETURN REQUEST - OTP GENERATED\n\n"
                f"The borrower ({borrow_request.borrower.name}) is ready to return your item.\n\n"
                f"They will show you a 6-digit OTP when returning.\n\n"
                f"⚠️ IMPORTANT: Only mark as returned AFTER verifying their OTP and inspecting the item!\n\n"
                f"📦 Item: {borrow_request.product.title}\n"
                f"⏰ OTP expires in 15 minutes"
            )
            
            # Create a system message intended specifically for the lender
            Message.objects.create(
                conversation=conversation,
                # Sender is borrower informing lender; recipient is lender
                sender=borrow_request.borrower,
                recipient=borrow_request.lender,
                content=message_to_lender,
                is_read=False,
                is_system_message=True,
                message_type='otp_return'
            )
        
        return True
    except Exception as e:
        print(f"Error sending OTP notification: {e}")
        return False


def format_otp_display(otp_code):
    """
    Format OTP code for display (e.g., "123 456" instead of "123456")
    
    Args:
        otp_code (str): OTP code
    
    Returns:
        str: Formatted OTP code
    """
    if len(otp_code) == 6:
        return f"{otp_code[:3]} {otp_code[3:]}"
    return otp_code


def get_otp_expiry_minutes(otp):
    """
    Get remaining minutes until OTP expiry
    
    Args:
        otp: BorrowOTP instance
    
    Returns:
        int: Minutes until expiry (0 if expired)
    """
    if otp.is_expired():
        return 0
    
    time_remaining = otp.expires_at - timezone.now()
    minutes = int(time_remaining.total_seconds() / 60)
    return max(0, minutes)


# ========================================
# PURCHASE OTP FUNCTIONS
# ========================================

def create_purchase_handover_otp(purchase_request):
    """
    Create a handover OTP for when buyer receives the purchased item
    Similar to Uber's pickup OTP
    
    Args:
        purchase_request: PurchaseRequest instance
    
    Returns:
        PurchaseOTP: Created OTP instance
    """
    from .models import PurchaseOTP
    
    # If there's an active (unverified & not expired) handover OTP, reuse it
    active = get_active_purchase_otp(purchase_request)
    if active:
        return active

    # Otherwise generate and persist a new OTP
    otp_code = generate_otp()
    otp = PurchaseOTP.objects.create(
        purchase_request=purchase_request,
        otp_code=otp_code,
        expires_at=timezone.now() + timedelta(minutes=15)
    )
    
    return otp


def get_active_purchase_otp(purchase_request):
    """
    Get the active (unverified, not expired) handover OTP for a purchase request
    
    Args:
        purchase_request: PurchaseRequest instance
    
    Returns:
        PurchaseOTP or None: Active OTP if exists
    """
    from .models import PurchaseOTP
    
    try:
        otp = PurchaseOTP.objects.filter(
            purchase_request=purchase_request,
            is_verified=False
        ).order_by('-created_at').first()
        
        if otp and otp.is_valid():
            return otp
        return None
    except PurchaseOTP.DoesNotExist:
        return None


def verify_purchase_otp(purchase_request, user, entered_otp):
    """
    Verify the handover OTP for a purchase request
    
    Args:
        purchase_request: PurchaseRequest instance
        user: User attempting to verify
        entered_otp: OTP code entered by user
    
    Returns:
        tuple: (success: bool, message: str, otp: PurchaseOTP or None)
    """
    from .models import PurchaseOTP
    
    # Get the latest active OTP
    otp = get_active_purchase_otp(purchase_request)
    
    if not otp:
        return False, "No active OTP found", None
    
    # Verify the OTP
    success, message = otp.verify(user, entered_otp)
    
    if success:
        # Update purchase request status
        with transaction.atomic():
            purchase_request.handover_otp_verified = True
            purchase_request.handover_otp_verified_at = timezone.now()
            purchase_request.status = 'completed'
            purchase_request.completed_date = timezone.now()
            purchase_request.save()
            
            # Mark product as unavailable (sold)
            purchase_request.product.is_available = False
            purchase_request.product.save()
    
    return success, message, otp


def send_purchase_otp_notification(purchase_request, notification_type='handover'):
    """
    Send OTP notification via chat for purchase transactions
    
    Args:
        purchase_request: PurchaseRequest instance
        notification_type: 'handover' for item transfer OTP
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from chat.models import Conversation, Message
    from django.db import transaction
    
    buyer = purchase_request.buyer
    seller = purchase_request.seller
    product = purchase_request.product
    
    # Get or create conversation
    try:
        conversation, created = Conversation.objects.get_or_create(
            product=product,
            buyer=buyer,
            seller=seller
        )
    except Exception as e:
        return False, f"Failed to create conversation: {str(e)}"
    
    try:
        with transaction.atomic():
            if notification_type == 'handover':
                # Generate handover OTP
                otp = create_purchase_handover_otp(purchase_request)
                otp_code_formatted = format_otp_display(otp.otp_code)
                
                # Send OTP to buyer (who will give it to seller)
                buyer_message = (
                    f"🎉 PURCHASE APPROVED!\n\n"
                    f"Your purchase of '{product.title}' has been approved by the seller.\n\n"
                    f"📱 HANDOVER OTP: {otp_code_formatted}\n\n"
                    f"Give this OTP to the seller during item handover to complete the purchase. "
                    f"The seller will verify this OTP to confirm you've received the item.\n\n"
                    f"⏰ Valid for 15 minutes"
                )
                Message.objects.create(
                    conversation=conversation,
                    sender=seller,  # From seller's side
                    recipient=buyer,  # Only buyer sees this
                    content=buyer_message,
                    is_system_message=True,
                    message_type='otp_handover'
                )
                
                # Notify seller about OTP generation
                buyer_display_name = buyer.name if buyer.name else buyer.email
                seller_message = (
                    f"📊 PURCHASE APPROVED - OTP GENERATED\n\n"
                    f"You approved {buyer_display_name}'s purchase request for '{product.title}'.\n\n"
                    f"The buyer has been sent a handover OTP. During item transfer, "
                    f"ask the buyer for the OTP and verify it in the purchase dashboard "
                    f"to complete the transaction.\n\n"
                    f"💰 Sale Price: ₹{purchase_request.purchase_price}"
                )
                Message.objects.create(
                    conversation=conversation,
                    sender=buyer,  # From buyer's side
                    recipient=seller,  # Only seller sees this
                    content=seller_message,
                    is_system_message=True,
                    message_type='otp_handover'
                )
                
                return True, "Handover OTP sent successfully"
            
    except Exception as e:
        return False, f"Failed to send notification: {str(e)}"
    
    return False, "Invalid notification type"
