from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Article, Categorie, Tag, Comment, Like, Bookmark, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'bio', 'avatar', 'website', 'twitter', 'date_created']
        read_only_fields = ['date_created']


class CategorieSerializer(serializers.ModelSerializer):
    """Serializer for Categorie model"""
    articles_count = serializers.ReadOnlyField(source='get_articles_count')
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'slug', 'couleur', 'icone', 
                 'date_creation', 'articles_count']
        read_only_fields = ['id', 'slug', 'date_creation']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'nom', 'slug', 'date_creation', 'article_count']
        read_only_fields = ['id', 'slug', 'date_creation']
    
    def get_article_count(self, obj):
        return obj.articles.filter(statut='published').count()


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for Article list view"""
    auteur = serializers.StringRelatedField()
    categorie = CategorieSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField(source='get_reading_time')
    likes_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Article
        fields = ['id', 'titre', 'slug', 'extrait', 'auteur', 'categorie', 'tags',
                 'statut', 'image', 'date_creation', 'date_modification', 
                 'vues', 'likes_count', 'reading_time']


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for Article detail view"""
    auteur = UserSerializer(read_only=True)
    categorie = CategorieSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField(source='get_reading_time')
    likes_count = serializers.ReadOnlyField()
    similar_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ['id', 'titre', 'slug', 'contenu', 'extrait', 'auteur', 'categorie', 
                 'tags', 'statut', 'image', 'date_creation', 'date_modification',
                 'vues', 'likes_count', 'meta_title', 'meta_description', 
                 'reading_time', 'similar_articles']
        read_only_fields = ['id', 'slug', 'auteur', 'date_creation', 'date_modification', 'vues']
    
    def get_similar_articles(self, obj):
        similar = obj.get_similar_articles()
        return ArticleListSerializer(similar, many=True, context=self.context).data


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Article creation and updates"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(),
        required=False
    )
    
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'extrait', 'categorie', 'tags', 'statut', 
                 'image', 'meta_title', 'meta_description']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tags_data)
        return article
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags_data is not None:
            instance.tags.set(tags_data)
        
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    author = UserSerializer(read_only=True)
    article_title = serializers.ReadOnlyField(source='article.titre')
    
    class Meta:
        model = Comment
        fields = ['id', 'article', 'article_title', 'nom', 'email', 'author', 
                 'contenu', 'statut', 'date_creation', 'date_moderation', 'moderateur']
        read_only_fields = ['id', 'author', 'date_creation', 'date_moderation', 'moderateur']
    
    def create(self, validated_data):
        # Set author if user is authenticated
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
            validated_data['nom'] = request.user.get_full_name() or request.user.username
            validated_data['email'] = request.user.email
        return Comment.objects.create(**validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""
    user = UserSerializer(read_only=True)
    article_title = serializers.ReadOnlyField(source='article.titre')
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'article', 'article_title', 'date_creation']
        read_only_fields = ['id', 'user', 'date_creation']


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for Bookmark model"""
    user = UserSerializer(read_only=True)
    article_title = serializers.ReadOnlyField(source='article.titre')
    
    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'article', 'article_title', 'date_creation']
        read_only_fields = ['id', 'user', 'date_creation']
