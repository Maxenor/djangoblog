from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware to handle role-based permissions.
    """
    
    # URLs that require specific roles
    ADMIN_REQUIRED_URLS = [
        '/admin/',
        '/ajouter/',
        '/modifier/',
        '/supprimer/',
        '/categories/ajouter/',
        '/categories/modifier/',
        '/categories/supprimer/',
    ]
    
    AUTHOR_REQUIRED_URLS = [
        '/dashboard/',
        '/mes-articles/',
    ]
    
    def process_request(self, request):
        """Check permissions for protected URLs"""
        try:
            # Skip if user is not authenticated
            if not request.user.is_authenticated:
                return None
            
            # Skip if user doesn't have a profile
            if not hasattr(request.user, 'profile'):
                return None
            
            path = request.path
            user_profile = request.user.profile
            
            # Check admin-required URLs
            for admin_url in self.ADMIN_REQUIRED_URLS:
                if path.startswith(admin_url):
                    if not user_profile.is_admin():
                        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                        return redirect('home')
            
            # Check author-required URLs
            for author_url in self.AUTHOR_REQUIRED_URLS:
                if path.startswith(author_url):
                    if not user_profile.is_author():
                        messages.error(request, "Accès réservé aux auteurs.")
                        return redirect('home')
                        
        except Exception as e:
            logger.error(f"Permission middleware error: {e}")
        
        return None
