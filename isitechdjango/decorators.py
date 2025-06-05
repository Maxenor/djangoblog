from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def superadmin_required(view_func):
    """
    Decorator to restrict access to superadmin users only.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_superadmin():
            messages.error(request, 'You do not have permission to access this page. Super admin access required.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def user_required(view_func):
    """
    Decorator to restrict access to authenticated users only.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view
