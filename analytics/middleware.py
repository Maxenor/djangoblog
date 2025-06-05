from django.utils.deprecation import MiddlewareMixin
from .models import PageView, ArticleView
import logging
import re

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to track page views for analytics.
    """
    
    def process_request(self, request):
        """Track page views"""
        try:
            # Skip admin and static files
            if request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path.startswith('/media/'):
                return None
            
            # Get client IP
            ip_address = self.get_client_ip(request)
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Get referrer
            referrer = request.META.get('HTTP_REFERER', '')
            
            # Get session key
            session_key = request.session.session_key or ''
            
            # Create page view record
            PageView.objects.create(
                user=request.user if request.user.is_authenticated else None,
                path=request.path,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                session_key=session_key
            )
            
            # Track article views separately
            self.track_article_view(request, ip_address, session_key)
            
        except Exception as e:
            logger.error(f"Analytics middleware error: {e}")
        
        return None
    
    def track_article_view(self, request, ip_address, session_key):
        """Track specific article views"""
        try:
            # Check if this is an article detail page
            article_pattern = r'/article/(\d+)/'
            match = re.match(article_pattern, request.path)
            
            if match:
                article_id = match.group(1)
                
                # Import here to avoid circular imports
                from isitechdjango.models import Article
                
                try:
                    article = Article.objects.get(id=article_id, statut='published')
                    
                    # Create article view record
                    ArticleView.objects.create(
                        article=article,
                        user=request.user if request.user.is_authenticated else None,
                        ip_address=ip_address,
                        session_key=session_key,
                        reading_time=0  # Will be updated via JavaScript
                    )
                    
                    # Increment article view count
                    article.vues += 1
                    article.save(update_fields=['vues'])
                    
                except Article.DoesNotExist:
                    pass
                    
        except Exception as e:
            logger.error(f"Article tracking error: {e}")
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
