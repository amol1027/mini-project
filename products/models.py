from django.db import models
from registration.models import User

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
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

