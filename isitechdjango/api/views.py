from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import Article, Categorie, Tag, Comment, Like, Bookmark
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer,
    CategorieSerializer, TagSerializer, CommentSerializer, 
    LikeSerializer, BookmarkSerializer
)
from .permissions import (
    IsAuthorOrReadOnly, IsEditorOrAuthorOrReadOnly, 
    IsAdminOrEditorOrReadOnly, IsOwnerOrReadOnly, CanModerateComments
)


class CategorieViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminOrEditorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'date_creation']
    ordering = ['nom']


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsEditorOrAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom', 'date_creation']
    ordering = ['nom']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular tags"""
        popular_tags = Tag.get_popular_tags(limit=20)
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles.
    """
    permission_classes = [IsEditorOrAuthorOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'categorie', 'auteur']
    search_fields = ['titre', 'contenu', 'extrait']
    ordering_fields = ['date_creation', 'date_modification', 'vues', 'likes_count']
    ordering = ['-date_creation']
    
    def get_queryset(self):
        """
        Filter articles based on user permissions.
        """
        queryset = Article.objects.all()
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.filter(statut='published')
        
        # If user is editor/admin, show all articles
        if hasattr(user, 'profile') and user.profile.is_editor():
            return queryset
        
        # For authors, show their own articles + published articles
        if hasattr(user, 'profile') and user.profile.is_author():
            return queryset.filter(
                Q(statut='published') | Q(auteur=user)
            )
        
        # For readers, only published articles
        return queryset.filter(statut='published')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        return ArticleDetailSerializer
    
    def perform_create(self, serializer):
        """
        Set the author to the current user when creating an article.
        """
        serializer.save(auteur=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Toggle like for an article"""
        article = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if not created:
            like.delete()
            return Response(
                {'message': 'Article unliked', 'liked': False}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Article liked', 'liked': True}, 
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        """Toggle bookmark for an article"""
        article = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if not created:
            bookmark.delete()
            return Response(
                {'message': 'Article unbookmarked', 'bookmarked': False}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Article bookmarked', 'bookmarked': True}, 
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_articles(self, request):
        """Get current user's articles"""
        articles = self.get_queryset().filter(auteur=request.user)
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def bookmarked(self, request):
        """Get current user's bookmarked articles"""
        bookmarked_articles = Article.objects.filter(
            bookmarks__user=request.user,
            statut='published'
        ).order_by('-bookmarks__date_creation')
        
        page = self.paginate_queryset(bookmarked_articles)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleListSerializer(bookmarked_articles, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'statut']
    ordering_fields = ['date_creation']
    ordering = ['date_creation']
    
    def get_queryset(self):
        """
        Filter comments based on user permissions.
        """
        user = self.request.user
        
        if hasattr(user, 'profile') and user.profile.is_editor():
            # Editors can see all comments
            return Comment.objects.all()
        
        # Regular users only see approved comments
        return Comment.objects.filter(statut='approved')
    
    def perform_create(self, serializer):
        """
        Set default status for new comments based on user role.
        """
        user = self.request.user
        
        # If user is editor/admin, auto-approve
        if hasattr(user, 'profile') and user.profile.is_editor():
            serializer.save(statut='approved')
        else:
            # Regular users' comments need moderation
            serializer.save(statut='pending')
    
    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[CanModerateComments],
        url_path='approve'
    )
    def approve_comment(self, request, pk=None):
        """Approve a comment"""
        comment = self.get_object()
        comment.approve(request.user)
        return Response(
            {'message': 'Comment approved'}, 
            status=status.HTTP_200_OK
        )
    
    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[CanModerateComments],
        url_path='reject'
    )
    def reject_comment(self, request, pk=None):
        """Reject a comment"""
        comment = self.get_object()
        comment.reject(request.user)
        return Response(
            {'message': 'Comment rejected'}, 
            status=status.HTTP_200_OK
        )


class LikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing likes (read-only).
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article']
    ordering = ['-date_creation']
    
    def get_queryset(self):
        """Return user's likes"""
        return Like.objects.filter(user=self.request.user)


class BookmarkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing bookmarks (read-only).
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article']
    ordering = ['-date_creation']
    
    def get_queryset(self):
        """Return user's bookmarks"""
        return Bookmark.objects.filter(user=self.request.user)
