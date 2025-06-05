from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import translation
from isitechdjango.models import Article, Categorie, Like, Bookmark, UserProfile
import json


class LikeBookmarkSystemTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Set language for URL generation
        translation.activate('en')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test category
        self.category = Categorie.objects.create(
            nom='Test Category',
            description='A test category'
        )
        
        # Create test article
        self.article = Article.objects.create(
            titre='Test Article',
            contenu='This is a test article content.',
            auteur=self.user,
            categorie=self.category,
            statut='published'
        )
        
        self.client = Client()
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created automatically"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'reader')
    
    def test_like_toggle_authenticated(self):
        """Test like toggle functionality for authenticated user"""
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Initially, article should have 0 likes
        self.assertEqual(self.article.likes_count, 0)
        
        # Test adding a like
        response = self.client.post(
            reverse('toggle_like', kwargs={'article_id': self.article.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        
        # Refresh article from database
        self.article.refresh_from_db()
        self.assertEqual(self.article.likes_count, 1)
        
        # Test that Like object was created
        self.assertTrue(Like.objects.filter(user=self.user, article=self.article).exists())
        
        # Test removing the like
        response = self.client.post(
            reverse('toggle_like', kwargs={'article_id': self.article.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)
        
        # Refresh article from database
        self.article.refresh_from_db()
        self.assertEqual(self.article.likes_count, 0)
        
        # Test that Like object was deleted
        self.assertFalse(Like.objects.filter(user=self.user, article=self.article).exists())
    
    def test_user_profile_view(self):
        """Test user profile view"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('user_profile', kwargs={'username': self.user.username})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
    
    def test_dashboard_view_for_author(self):
        """Test dashboard view for author role"""
        # Make user an author
        self.user.profile.role = 'author'
        self.user.profile.save()
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Auteur')


class ArticleModelTest(TestCase):
    def setUp(self):
        translation.activate('en')
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Categorie.objects.create(
            nom='Test Category'
        )
        
        self.article = Article.objects.create(
            titre='Test Article',
            contenu='This is a long test article content that should take some time to read. ' * 50,
            auteur=self.user,
            categorie=self.category,
            statut='published'
        )
    
    def test_reading_time_calculation(self):
        """Test reading time calculation"""
        reading_time = self.article.get_reading_time()
        self.assertGreater(reading_time, 0)
        self.assertIsInstance(reading_time, int)
    
    def test_slug_generation(self):
        """Test automatic slug generation"""
        self.assertTrue(self.article.slug)
        self.assertIn('test-article', self.article.slug.lower())
