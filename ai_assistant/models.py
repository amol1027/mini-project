from django.db import models
from registration.models import User


class ChatSession(models.Model):
    """
    Represents a chat session between a user and the AI assistant
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ai_chat_sessions',
        null=True, 
        blank=True,
        help_text="User who initiated the chat (null for anonymous users)"
    )
    session_key = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Session key for anonymous users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
    
    def __str__(self):
        if self.user:
            return f"Chat with {self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        return f"Anonymous Chat - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """
    Individual messages in a chat session
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Store metadata like intent detected, confidence score, etc.
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class FAQEntry(models.Model):
    """
    Pre-defined FAQ entries for common questions
    The AI assistant uses these to provide accurate responses
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('products', 'Products & Listings'),
        ('borrowing', 'Borrowing & Lending'),
        ('account', 'Account & Profile'),
        ('payment', 'Payment & Transactions'),
        ('safety', 'Safety & Guidelines'),
        ('technical', 'Technical Support'),
    ]
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    keywords = models.TextField(
        help_text="Comma-separated keywords for matching",
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'question']
        verbose_name = 'FAQ Entry'
        verbose_name_plural = 'FAQ Entries'
    
    def __str__(self):
        return self.question[:100]
    
    def get_keywords_list(self):
        """Return keywords as a list"""
        if self.keywords:
            return [k.strip().lower() for k in self.keywords.split(',')]
        return []
