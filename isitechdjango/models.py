from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """
    Model representing user profiles with roles.
    """
    ROLE_CHOICES = [
        ('reader', 'Lecteur'),
        ('author', 'Auteur'),
        ('editor', 'Éditeur'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')
    date_created = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True, help_text="Biographie de l'utilisateur")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_editor(self):
        return self.role in ['editor', 'admin']
    
    def is_author(self):
        return self.role in ['author', 'editor', 'admin']
    
    def is_reader(self):
        return self.role == 'reader'
    
    # Legacy methods for backward compatibility
    def is_superadmin(self):
        return self.role == 'admin'
    
    def is_regular_user(self):
        return self.role == 'reader'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a UserProfile when a User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

class Categorie(models.Model):
    """
    Model representing a category for articles.
    """
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    couleur = models.CharField(max_length=7, default='#007bff', help_text='Code couleur hexadécimal (ex: #ff5733)')
    icone = models.CharField(max_length=50, default='fas fa-folder', help_text='Classe CSS pour l\'icône (ex: fas fa-folder)')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    def get_articles_count(self):
        return self.articles.filter(statut='published').count()
    
    def get_total_views(self):
        """Get total views for all articles in this category"""
        return self.articles.filter(statut='published').aggregate(
            total_views=models.Sum('vues')
        )['total_views'] or 0
    
    def get_total_likes(self):
        """Get total likes for all articles in this category"""
        return self.articles.filter(statut='published').aggregate(
            total_likes=models.Sum('likes_count')
        )['total_likes'] or 0
    
    def get_top_articles(self, limit=5):
        """Get top articles in this category by views"""
        return self.articles.filter(statut='published').order_by('-vues', '-likes_count')[:limit]
    
    def get_recent_articles(self, limit=5):
        """Get most recent articles in this category"""
        return self.articles.filter(statut='published').order_by('-date_creation')[:limit]
    
    class Meta:
        ordering = ['nom']


class Tag(models.Model):
    """
    Model representing a tag for articles.
    """
    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_popular_tags(cls, limit=10):
        """Retourne les tags les plus populaires basés sur le nombre d'articles"""
        from django.db.models import Count
        return cls.objects.annotate(
            article_count=Count('articles')
        ).filter(article_count__gt=0).order_by('-article_count')[:limit]
    
    @classmethod
    def get_trending_tags(cls, limit=10):
        """Get trending tags based on recent usage and engagement"""
        from django.db.models import Count, Sum, Avg
        from datetime import datetime, timedelta
        
        recent_date = datetime.now() - timedelta(days=30)
        
        return cls.objects.annotate(
            recent_usage=Count('articles', filter=models.Q(articles__date_creation__gte=recent_date)),
            total_articles=Count('articles'),
            avg_views=Avg('articles__vues'),
            total_likes=Sum('articles__likes_count')
        ).filter(total_articles__gt=0).order_by('-recent_usage', '-avg_views')[:limit]
    
    def get_article_count(self):
        """Get number of published articles with this tag"""
        return self.articles.filter(statut='published').count()
    
    def get_engagement_score(self):
        """Calculate engagement score based on views and likes"""
        articles = self.articles.filter(statut='published')
        if not articles.exists():
            return 0
        
        total_views = articles.aggregate(total=models.Sum('vues'))['total'] or 0
        total_likes = articles.aggregate(total=models.Sum('likes_count'))['total'] or 0
        article_count = articles.count()
        
        # Score = (average views + average likes * 5) per article
        return int((total_views + total_likes * 5) / article_count) if article_count > 0 else 0
    
    class Meta:
        ordering = ['nom']


class Article(models.Model):
    """
    Model representing an article.
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    contenu = models.TextField()
    extrait = models.TextField(max_length=300, blank=True, help_text="Résumé de l'article")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, help_text='Image de couverture')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    vues = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    
    # SEO Meta fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="Titre SEO (max 60 caractères)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Description SEO (max 160 caractères)")

    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        
        if not self.slug:
            base_slug = slugify(self.titre)
            unique_slug = base_slug
            num = 1
            while Article.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        
        # Auto-generate extrait if not provided
        if not self.extrait and self.contenu:
            import re
            # Remove HTML tags and truncate
            clean_content = re.sub('<.*?>', '', self.contenu)
            self.extrait = clean_content[:300]
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = self.titre[:60]
        if not self.meta_description:
            self.meta_description = self.extrait[:160] if self.extrait else self.titre[:160]
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count"""
        self.vues += 1
        self.save(update_fields=['vues'])
    
    def get_reading_time(self):
        """Calculate estimated reading time in minutes"""
        import re
        word_count = len(re.findall(r'\w+', self.contenu))
        return max(1, word_count // 200)  # Assuming 200 words per minute
    
    def get_similar_articles(self, limit=3, user=None):
        """
        Get similar articles based on category, tags, user preferences, and popularity
        Enhanced intelligent recommendation algorithm
        """
        from django.db.models import Count, Q, Case, When, IntegerField, F
        
        similar = Article.objects.filter(
            statut='published'
        ).exclude(id=self.id)
        
        # Base scoring system
        similar = similar.annotate(
            similarity_score=Case(
                # Same category gets highest score
                When(categorie=self.categorie, then=50),
                default=0,
                output_field=IntegerField()
            )
        )
        
        # Add tag-based similarity scoring
        if self.tags.exists():
            tag_ids = list(self.tags.values_list('id', flat=True))
            similar = similar.annotate(
                tag_matches=Count(
                    'tags',
                    filter=Q(tags__id__in=tag_ids)
                )
            ).annotate(
                tag_score=F('tag_matches') * 10  # 10 points per matching tag
            ).annotate(
                similarity_score=F('similarity_score') + F('tag_score')
            )
        
        # Add popularity bonus (views and likes)
        similar = similar.annotate(
            popularity_score=Case(
                When(vues__gte=100, then=15),  # High view count
                When(vues__gte=50, then=10),   # Medium view count
                When(vues__gte=10, then=5),    # Low view count
                default=0,
                output_field=IntegerField()
            ) + Case(
                When(likes_count__gte=10, then=10),  # High likes
                When(likes_count__gte=5, then=5),    # Medium likes
                When(likes_count__gte=1, then=2),    # Some likes
                default=0,
                output_field=IntegerField()
            )
        ).annotate(
            similarity_score=F('similarity_score') + F('popularity_score')
        )
        
        # Add user preference scoring if user is provided
        if user and user.is_authenticated:
            # Get user's liked categories and tags
            user_liked_articles = user.likes.values_list('article', flat=True)
            user_bookmarked_articles = user.bookmarks.values_list('article', flat=True)
            
            # Bonus for articles from same authors user has liked/bookmarked
            preferred_authors = Article.objects.filter(
                Q(id__in=user_liked_articles) | Q(id__in=user_bookmarked_articles)
            ).values_list('auteur', flat=True).distinct()
            
            similar = similar.annotate(
                user_preference_score=Case(
                    When(auteur__in=preferred_authors, then=20),  # Preferred author bonus
                    default=0,
                    output_field=IntegerField()
                )
            ).annotate(
                similarity_score=F('similarity_score') + F('user_preference_score')
            )
        
        # Add recency bonus for newer articles
        from datetime import datetime, timedelta
        recent_date = datetime.now() - timedelta(days=30)
        
        similar = similar.annotate(
            recency_score=Case(
                When(date_creation__gte=recent_date, then=5),  # Recent articles bonus
                default=0,
                output_field=IntegerField()
            )
        ).annotate(
            final_score=F('similarity_score') + F('recency_score')
        )
        
        # Order by final score and limit results
        return similar.order_by('-final_score', '-date_creation')[:limit]
    
    class Meta:
        ordering = ['-date_creation']


class Comment(models.Model):
    """
    Model representing a comment on an article.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    contenu = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_moderation = models.DateTimeField(null=True, blank=True)
    moderateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_comments')
    
    def __str__(self):
        if self.author:
            return f'Commentaire de {self.author.username} sur {self.article.titre}'
        else:
            return f'Commentaire de {self.nom} sur {self.article.titre}'
    
    def approve(self, moderator):
        """Approve the comment"""
        self.statut = 'approved'
        self.moderateur = moderator
        from django.utils import timezone
        self.date_moderation = timezone.now()
        self.save()
    
    def reject(self, moderator):
        """Reject the comment"""
        self.statut = 'rejected'
        self.moderateur = moderator
        from django.utils import timezone
        self.date_moderation = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['date_creation']


class Like(models.Model):
    """
    Model representing a like on an article.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'article')
        ordering = ['-date_creation']
    
    def __str__(self):
        return f'{self.user.username} likes {self.article.titre}'


class Bookmark(models.Model):
    """
    Model representing a bookmark on an article.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarks')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'article')
        ordering = ['-date_creation']
    
    def __str__(self):
        return f'{self.user.username} bookmarked {self.article.titre}'