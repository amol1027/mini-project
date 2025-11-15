from django.db import models
from django.core.validators import MinValueValidator
from registration.models import User
from django.utils import timezone
from django.db import transaction, IntegrityError
from datetime import timedelta
import os

# Import ProductHistory model
from .history_models import ProductHistory

def product_image_upload_path(instance, filename):
    """
    Generate upload path for product images
    Format: products/<seller_id>/<product_id>/<filename>
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.title[:50]}_{instance.id or 'new'}.{ext}"
    return os.path.join('products', str(instance.seller.id), filename)

class Product(models.Model):
    """
    Product model for Student Resource Exchange
    Educational resources like books, notes, calculators, etc.
    """
    CATEGORY_CHOICES = [
        ('books', 'Books'),
        ('notes', 'Notes'),
        ('electronics', 'Electronics'),
        ('stationery', 'Stationery'),
        ('lab_equipment', 'Lab Equipment'),
        ('other', 'Other'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    LISTING_TYPE_CHOICES = [
        ('sell', 'For Sale'),
        ('lend', 'For Lending'),
        ('both', 'Sale or Lend'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Product name or title")
    description = models.TextField(help_text="Detailed description of the product")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    # Listing Type
    listing_type = models.CharField(
        max_length=10, 
        choices=LISTING_TYPE_CHOICES, 
        default='sell',
        help_text="Whether this item is for sale, lending, or both"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price in INR (₹) - for selling",
        blank=True,
        null=True
    )
    
    # Borrow/Lend specific fields
    borrow_price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Daily rental price in INR (₹)",
        blank=True,
        null=True
    )
    borrow_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Refundable deposit amount in INR (₹)",
        blank=True,
        null=True,
        default=0
    )
    max_borrow_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of days item can be borrowed"
    )
    is_currently_borrowed = models.BooleanField(
        default=False,
        help_text="Is this item currently borrowed by someone?"
    )
    
    # Images (up to 5 images per product)
    image1 = models.ImageField(
        upload_to=product_image_upload_path, 
        blank=True, 
        null=True,
        help_text="Primary product image (required)"
    )
    image2 = models.ImageField(
        upload_to=product_image_upload_path, 
        blank=True, 
        null=True,
        help_text="Additional image (optional)"
    )
    image3 = models.ImageField(
        upload_to=product_image_upload_path, 
        blank=True, 
        null=True,
        help_text="Additional image (optional)"
    )
    image4 = models.ImageField(
        upload_to=product_image_upload_path, 
        blank=True, 
        null=True,
        help_text="Additional image (optional)"
    )
    image5 = models.ImageField(
        upload_to=product_image_upload_path, 
        blank=True, 
        null=True,
        help_text="Additional image (optional)"
    )
    
    # Seller and Availability
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True, help_text="Is this product still available?")
    views = models.IntegerField(default=0, editable=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return self.title
    
    def get_primary_image(self):
        """Return the primary image or first available image"""
        # Try to return image1 first, then fallback to any available image
        if self.image1:
            return self.image1
        for i in range(2, 6):
            img = getattr(self, f'image{i}')
            if img:
                return img
        return None
    
    def get_all_images(self):
        """Return list of all non-null images"""
        images = []
        for i in range(1, 6):
            img = getattr(self, f'image{i}')
            if img:
                images.append(img)
        return images
    
    def has_images(self):
        """Check if product has at least one image"""
        return bool(self.image1)
    
    def can_be_borrowed(self):
        """Check if product is available for borrowing"""
        return (self.listing_type in ['lend', 'both'] and 
                self.is_available and 
                not self.is_currently_borrowed)
    
    def can_be_purchased(self):
        """Check if product is available for purchase"""
        return (self.listing_type in ['sell', 'both'] and 
                self.is_available and 
                not self.is_currently_borrowed)
    
    def save(self, *args, **kwargs):
        """Override save to track product history"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create history entry
        if is_new:
            ProductHistory.objects.create(
                product_id=self.id,
                title=self.title,
                description=self.description,
                category=self.category,
                condition=self.condition,
                listing_type=self.listing_type,
                price=self.price,
                user=self.seller,
                action='created',
                views_at_action=self.views,
                was_available=self.is_available
            )
    
    def delete(self, *args, **kwargs):
        """Override delete to track product history"""
        # Create history entry before deletion
        ProductHistory.objects.create(
            product_id=self.id,
            title=self.title,
            description=self.description,
            category=self.category,
            condition=self.condition,
            listing_type=self.listing_type,
            price=self.price,
            user=self.seller,
            action='deleted',
            views_at_action=self.views,
            was_available=self.is_available,
            reason=kwargs.pop('reason', None)
        )
        super().delete(*args, **kwargs)


class BorrowRequest(models.Model):
    """
    Model to track borrow/lend requests and transactions
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active - Item Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='borrow_requests'
    )
    borrower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='borrow_requests_made'
    )
    lender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='borrow_requests_received'
    )
    
    # Request Details
    requested_days = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of days requested to borrow"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    message = models.TextField(
        blank=True, 
        null=True,
        help_text="Message from borrower to lender"
    )
    
    # Financial
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total cost (daily rate × days)"
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Deposit amount"
    )
    
    # Dates
    request_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    expected_return_date = models.DateField(blank=True, null=True)
    actual_return_date = models.DateField(blank=True, null=True)
    
    # Response from lender
    lender_response = models.TextField(
        blank=True,
        null=True,
        help_text="Response message from lender"
    )
    
    # OTP Verification Status (Uber-style)
    acceptance_otp_verified = models.BooleanField(
        default=False,
        help_text="Whether acceptance OTP has been verified (item pickup confirmed)"
    )
    acceptance_otp_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When acceptance OTP was verified"
    )
    return_otp_verified = models.BooleanField(
        default=False,
        help_text="Whether return OTP has been verified (item return confirmed)"
    )
    return_otp_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When return OTP was verified"
    )
    
    # Location Sharing (NEW)
    lender_shares_location = models.BooleanField(
        default=False,
        help_text="Whether lender has agreed to share precise location for this request"
    )
    borrower_shares_location = models.BooleanField(
        default=False,
        help_text="Whether borrower has agreed to share precise location for this request"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'borrow_requests'
        ordering = ['-created_at']
        verbose_name = 'Borrow Request'
        verbose_name_plural = 'Borrow Requests'
    
    def __str__(self):
        return f"{self.borrower.name} wants to borrow {self.product.title}"
    
    def is_overdue(self):
        """Check if the borrowed item is overdue"""
        from django.utils import timezone
        if self.status == 'active' and self.expected_return_date:
            return timezone.now().date() > self.expected_return_date
        return False
    
    def calculate_total_cost(self):
        """Calculate total borrowing cost"""
        if self.product.borrow_price_per_day:
            return self.product.borrow_price_per_day * self.requested_days
        return 0


class BorrowOTP(models.Model):
    """
    OTP model for Uber-style verification during borrow acceptance and return
    Similar to how Uber uses OTP to verify rider pickup and drop-off
    """
    OTP_TYPE_CHOICES = [
        ('acceptance', 'Acceptance OTP'),  # When borrower picks up item
        ('return', 'Return OTP'),          # When borrower returns item
    ]
    
    # Relationships
    borrow_request = models.ForeignKey(
        BorrowRequest,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    
    # OTP Details
    otp_type = models.CharField(
        max_length=20,
        choices=OTP_TYPE_CHOICES,
        help_text="Type of OTP - acceptance or return"
    )
    otp_code = models.CharField(
        max_length=6,
        help_text="6-digit OTP code"
    )
    
    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether OTP has been successfully verified"
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When OTP was verified"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_otps',
        help_text="User who verified the OTP"
    )
    
    # Expiry and Attempts
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="OTP expiry time (default 15 minutes)"
    )
    attempts = models.IntegerField(
        default=0,
        help_text="Number of verification attempts"
    )
    max_attempts = models.IntegerField(
        default=5,
        help_text="Maximum allowed verification attempts"
    )
    
    class Meta:
        db_table = 'borrow_otps'
        ordering = ['-created_at']
        verbose_name = 'Borrow OTP'
        verbose_name_plural = 'Borrow OTPs'
        indexes = [
            models.Index(fields=['borrow_request', 'otp_type', '-created_at']),
            models.Index(fields=['otp_code', 'is_verified']),
        ]
    
    def __str__(self):
        status = "Verified" if self.is_verified else "Pending"
        return f"{self.otp_type.title()} OTP for {self.borrow_request} - {status}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is still valid for verification"""
        return (
            not self.is_verified and
            not self.is_expired() and
            self.attempts < self.max_attempts
        )
    
    def verify(self, user, entered_otp):
        """
        Verify the OTP code
        Returns tuple: (success: bool, message: str)
        """
        # Increment attempts
        self.attempts += 1
        self.save(update_fields=['attempts'])
        
        # Check if already verified
        if self.is_verified:
            return False, "OTP already verified"
        
        # Check if expired
        if self.is_expired():
            return False, "OTP has expired"
        
        # Check if max attempts exceeded
        if self.attempts > self.max_attempts:
            return False, "Maximum verification attempts exceeded"
        
        # Verify OTP code
        if self.otp_code == entered_otp:
            # Use an atomic transaction and assign FK by id to avoid
            # potential FK constraint issues when saving the relation.
            try:
                with transaction.atomic():
                    self.is_verified = True
                    self.verified_at = timezone.now()
                    # Ensure user has a primary key
                    if not getattr(user, 'pk', None):
                        return False, "Invalid verifier user"
                    # Assign by id to make the DB write explicit
                    self.verified_by_id = user.pk
                    self.save(update_fields=['is_verified', 'verified_at', 'verified_by'])
                return True, "OTP verified successfully"
            except IntegrityError as e:
                # Return a clearer message instead of bubbling up the DB exception
                return False, "Database error during OTP verification"
        else:
            remaining_attempts = self.max_attempts - self.attempts
            if remaining_attempts > 0:
                return False, f"Invalid OTP. {remaining_attempts} attempts remaining"
            else:
                return False, "Invalid OTP. Maximum attempts exceeded"
    
    def save(self, *args, **kwargs):
        """Set expiry time on creation"""
        if not self.pk and not self.expires_at:
            # OTP expires in 15 minutes by default
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)


class PurchaseRequest(models.Model):
    """
    Model to track buy/sell requests and transactions
    Similar to BorrowRequest but for purchasing products
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved - Awaiting Pickup'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed - Item Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchase_requests'
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase_requests_made'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase_requests_received'
    )
    
    # Request Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Message from buyer to seller"
    )
    
    # Financial
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Agreed purchase price"
    )
    
    # Dates
    request_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    # Response from seller
    seller_response = models.TextField(
        blank=True,
        null=True,
        help_text="Response message from seller"
    )
    
    # OTP Verification Status (Uber-style)
    handover_otp_verified = models.BooleanField(
        default=False,
        help_text="Whether handover OTP has been verified (item transfer confirmed)"
    )
    handover_otp_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When handover OTP was verified"
    )
    
    # Location Sharing (NEW)
    seller_shares_location = models.BooleanField(
        default=False,
        help_text="Whether seller has agreed to share precise location for this request"
    )
    buyer_shares_location = models.BooleanField(
        default=False,
        help_text="Whether buyer has agreed to share precise location for this request"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_requests'
        ordering = ['-created_at']
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'
    
    def __str__(self):
        return f"{self.buyer.name} wants to buy {self.product.title}"
    
    def is_expired(self):
        """
        Check if approved request has expired (24 hours without OTP verification)
        """
        if self.status == 'approved' and self.approved_date and not self.handover_otp_verified:
            expiry_time = self.approved_date + timedelta(hours=24)
            return timezone.now() > expiry_time
        return False
    
    def can_be_cancelled_by_buyer(self):
        """Check if buyer can cancel this request"""
        return self.status in ['pending', 'approved']
    
    def can_be_cancelled_by_seller(self):
        """Check if seller can cancel this request (after approval if handover doesn't happen)"""
        return self.status == 'approved' and not self.handover_otp_verified


class PurchaseOTP(models.Model):
    """
    OTP model for Uber-style verification during purchase handover
    Similar to BorrowOTP but for purchase transactions
    """
    # Relationships
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    
    # OTP Details
    otp_code = models.CharField(
        max_length=6,
        help_text="6-digit OTP code for handover verification"
    )
    
    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether OTP has been successfully verified"
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When OTP was verified"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_purchase_otps',
        help_text="User who verified the OTP"
    )
    
    # Expiry and Attempts
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="OTP expiry time (default 15 minutes)"
    )
    attempts = models.IntegerField(
        default=0,
        help_text="Number of verification attempts"
    )
    max_attempts = models.IntegerField(
        default=5,
        help_text="Maximum allowed verification attempts"
    )
    
    class Meta:
        db_table = 'purchase_otps'
        ordering = ['-created_at']
        verbose_name = 'Purchase OTP'
        verbose_name_plural = 'Purchase OTPs'
        indexes = [
            models.Index(fields=['purchase_request', '-created_at']),
            models.Index(fields=['otp_code', 'is_verified']),
        ]
    
    def __str__(self):
        status = "Verified" if self.is_verified else "Pending"
        return f"Handover OTP for {self.purchase_request} - {status}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is still valid for verification"""
        return (
            not self.is_verified and
            not self.is_expired() and
            self.attempts < self.max_attempts
        )
    
    def time_remaining_minutes(self):
        """Get remaining minutes until expiry"""
        if self.is_expired():
            return 0
        remaining = (self.expires_at - timezone.now()).total_seconds() / 60
        return max(0, int(remaining))
    
    def verify(self, user, entered_otp):
        """
        Verify the OTP code
        Returns tuple: (success: bool, message: str)
        """
        # Increment attempts
        self.attempts += 1
        self.save(update_fields=['attempts'])
        
        # Check if already verified
        if self.is_verified:
            return False, "OTP already verified"
        
        # Check if expired
        if self.is_expired():
            return False, "OTP has expired"
        
        # Check if max attempts exceeded
        if self.attempts > self.max_attempts:
            return False, "Maximum verification attempts exceeded"
        
        # Verify OTP code
        if self.otp_code == entered_otp:
            try:
                with transaction.atomic():
                    self.is_verified = True
                    self.verified_at = timezone.now()
                    if not getattr(user, 'pk', None):
                        return False, "Invalid verifier user"
                    self.verified_by_id = user.pk
                    self.save(update_fields=['is_verified', 'verified_at', 'verified_by'])
                return True, "OTP verified successfully"
            except IntegrityError as e:
                return False, "Database error during OTP verification"
        else:
            remaining_attempts = self.max_attempts - self.attempts
            if remaining_attempts > 0:
                return False, f"Invalid OTP. {remaining_attempts} attempts remaining"
            else:
                return False, "Invalid OTP. Maximum attempts exceeded"
    
    def save(self, *args, **kwargs):
        """Set expiry time on creation"""
        if not self.pk and not self.expires_at:
            # OTP expires in 15 minutes by default
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

