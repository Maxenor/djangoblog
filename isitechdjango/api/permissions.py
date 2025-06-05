from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the article.
        return obj.auteur == request.user


class IsEditorOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow editors and authors to modify content.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
            
        # Allow if user is an author, editor, or admin
        return hasattr(request.user, 'profile') and request.user.profile.is_author()
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Allow if user is the author or an editor/admin
        if hasattr(obj, 'auteur'):
            return (obj.auteur == request.user or 
                   (hasattr(request.user, 'profile') and request.user.profile.is_editor()))
        
        return hasattr(request.user, 'profile') and request.user.profile.is_author()


class IsAdminOrEditorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins and editors to modify.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
            
        return hasattr(request.user, 'profile') and request.user.profile.is_editor()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class CanModerateComments(permissions.BasePermission):
    """
    Custom permission for comment moderation.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Only editors and admins can moderate
        return hasattr(request.user, 'profile') and request.user.profile.is_editor()
