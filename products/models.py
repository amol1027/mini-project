from django.db import models
from django.core.validators import MinValueValidator
from registration.models import User
import os

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
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Product name or title")
    description = models.TextField(help_text="Detailed description of the product")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price in INR (₹)"
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
        """Return the primary image or None"""
        return self.image1 if self.image1 else None
    
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

