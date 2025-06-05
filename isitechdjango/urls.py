from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import HomeRedirectView

urlpatterns = [
    path('', HomeRedirectView.as_view(), name='home_redirect'),
    path('home/', views.home, name='home'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('article/modifier/<int:article_id>/', views.modifier_article, name='modifier_article'),
    path('article/supprimer/<int:article_id>/', views.supprimer_article, name='supprimer_article'),
    path('categories/', views.categories, name='categories'),
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
    path('categories/modifier/<int:categorie_id>/', views.modifier_categorie, name='modifier_categorie'),
    path('categories/supprimer/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Enhanced Search System
    path('search/', views.search_results, name='search_results'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Like and Bookmark system
    path('article/<int:article_id>/like/', views.toggle_like, name='toggle_like'),
    path('article/<int:article_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('article/<int:article_id>/toggle-status/', views.toggle_article_status, name='toggle_article_status'),
    
    # User profiles and dashboard
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Comment moderation
    path('moderation/comments/', views.comment_moderation, name='comment_moderation'),
    path('moderate-comment/<int:comment_id>/', views.moderate_comment_individual, name='moderate_comment_individual'),
    path('bulk-moderate-comments/', views.bulk_moderate_comments, name='bulk_moderate_comments'),
    
    # AI Article Generator
    path('ai-generator/', views.ai_article_generator, name='ai_article_generator'),
    
    # Password reset URLs using Django's built-in views
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
