from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ArticleViewSet, CategorieViewSet, TagViewSet, 
    CommentViewSet, LikeViewSet, BookmarkViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'categories', CategorieViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes
    path('', include(router.urls)),
]
