from django.db import models
from django.core.validators import MinValueValidator
from registration.models import User
from django.utils import timezone


class ProductHistory(models.Model):
    """
    Track product listing and deletion history for audit purposes
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('sold', 'Sold'),
    ]
    
    # Product details (snapshot at time of action)
    product_id = models.IntegerField(help_text="Original product ID")
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50)
    condition = models.CharField(max_length=20)
    listing_type = models.CharField(max_length=10)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # User who performed the action
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='product_history'
    )
    
    # Action tracking
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    action_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Optional reason for deletion or update"
    )
    
    # Metadata
    views_at_action = models.IntegerField(default=0)
    was_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_history'
        ordering = ['-action_date']
        verbose_name = 'Product History'
        verbose_name_plural = 'Product Histories'
        indexes = [
            models.Index(fields=['user', '-action_date']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.action} - {self.title}"
    
    def get_action_display_color(self):
        """Return color class for action badge"""
        colors = {
            'created': 'bg-green-100 text-green-800',
            'updated': 'bg-blue-100 text-blue-800',
            'deleted': 'bg-red-100 text-red-800',
            'sold': 'bg-purple-100 text-purple-800',
        }
        return colors.get(self.action, 'bg-gray-100 text-gray-800')
