from django.db import models
from django.db.models import Q
from registration.models import User
from products.models import Product


class NotificationPreference(models.Model):
    """
    User preferences for chat notifications
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    enable_sound = models.BooleanField(
        default=True,
        help_text="Play sound when receiving messages"
    )
    enable_desktop = models.BooleanField(
        default=True,
        help_text="Show desktop notifications"
    )
    enable_email = models.BooleanField(
        default=False,
        help_text="Send email notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_notification_preference'
    
    def __str__(self):
        return f"Notification preferences for {self.user.name or self.user.email}"


class Conversation(models.Model):
    """
    Represents a conversation between a buyer and seller about a product
    """
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buyer_conversations',
        help_text="User interested in buying the product"
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seller_conversations',
        help_text="User who owns/sells the product"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='conversations',
        help_text="Product being discussed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_conversation'
        ordering = ['-updated_at']
        # Ensure unique conversation per buyer-seller-product combination
        unique_together = ['buyer', 'seller', 'product']
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['buyer', 'seller']),
        ]
    
    def __str__(self):
        return f"Conversation: {self.buyer.name} - {self.seller.name} (Product: {self.product.title})"
    
    def get_last_message(self):
        """Get the most recent message in the conversation"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Get count of unread messages for a specific user"""
        return self.messages.exclude(sender=user).filter(is_read=False).count()
    
    @staticmethod
    def get_total_unread_count(user):
        """Get total unread message count across all conversations for a user"""
        return Message.objects.filter(
            Q(conversation__buyer=user) | Q(conversation__seller=user)
        ).exclude(sender=user).filter(is_read=False).count()


class Message(models.Model):
    """
    Individual messages within a conversation
    """
    MESSAGE_TYPE_CHOICES = [
        ('regular', 'Regular Message'),
        ('otp_handover', 'Handover OTP'),
        ('otp_return', 'Return OTP'),
        ('system', 'System Notification'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="The conversation this message belongs to"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    content = models.TextField(help_text="Message content")
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read")
    is_system_message = models.BooleanField(
        default=False,
        help_text="Whether this is a system-generated message (e.g., OTP)"
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='regular',
        help_text="Type of message"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_messages',
        help_text="Intended recipient for system messages (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.name}: {self.content[:50]}"
    
    def mark_as_read(self):
        """Mark this message as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
