from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta


class PageView(models.Model):
    """
    Model to track page views for analytics.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f'{self.path} - {self.timestamp}'
    
    @classmethod
    def get_popular_pages(cls, limit=10):
        """Get most popular pages"""
        return cls.objects.values('path').annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:limit]
    
    @classmethod
    def get_unique_visitors(cls, days=30):
        """Get unique visitors count for the last N days"""
        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            timestamp__gte=since
        ).values('ip_address').distinct().count()
    
    @classmethod
    def get_traffic_sources(cls, limit=10):
        """Get top traffic sources"""
        return cls.objects.exclude(
            referrer=''
        ).values('referrer').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]


class ArticleView(models.Model):
    """
    Model to track specific article views.
    """
    article = models.ForeignKey('isitechdjango.Article', on_delete=models.CASCADE, related_name='analytics_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reading_time = models.PositiveIntegerField(default=0, help_text="Time spent reading in seconds")
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.article.titre} - {self.timestamp}'
