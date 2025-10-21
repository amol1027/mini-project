from django.db import models
from django.core.validators import MinValueValidator
from registration.models import User
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

