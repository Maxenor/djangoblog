from django.db import models
from django.contrib.auth.models import User
from isitechdjango.models import Article, Comment


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', 'Article Like'),
        ('comment', 'New Comment'),
        ('comment_approved', 'Comment Approved'),
        ('comment_rejected', 'Comment Rejected'),
        ('new_article', 'New Article from Followed Author'),
    ]
    
    # Who receives the notification
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Who triggered the notification  
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_notifications', null=True, blank=True)
    
    # Type of notification
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Message/title for the notification
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Notification status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = models.timezone.now()
            self.save()
    
    def get_url(self):
        """Get the URL to redirect to when clicking the notification"""
        if self.article:
            return self.article.get_absolute_url()
        elif self.comment and self.comment.article:
            return f"{self.comment.article.get_absolute_url()}#comment-{self.comment.id}"
        return '/'


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notification preferences
    email_on_like = models.BooleanField(default=True)
    email_on_comment = models.BooleanField(default=True)
    email_on_comment_approved = models.BooleanField(default=True)
    email_on_new_article = models.BooleanField(default=False)
    
    # In-app notification preferences (always on by default)
    notify_on_like = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_comment_approved = models.BooleanField(default=True)
    notify_on_new_article = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
