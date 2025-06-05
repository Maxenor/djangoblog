from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
import json
import traceback
import google.generativeai as genai
from django.conf import settings
from .models import Article, Comment, Categorie, UserProfile, Like, Bookmark
from .forms import ArticleForm, CommentForm, CategorieForm, UserRegisterForm, UserLoginForm, AdvancedSearchForm
from .decorators import superadmin_required, user_required
from .search_utils import SearchEngine, SearchFilter

@user_required
def home(request):
    """Enhanced home view with advanced search and filtering"""
    search_filter = SearchFilter(request)
    search_form = AdvancedSearchForm(request.GET)
    
    # Get articles using the advanced search engine
    articles = SearchEngine.search_articles(
        query=search_filter.query,
        category_id=search_filter.category_id,
        author_id=search_filter.author_id,
        tag_ids=search_filter.tag_ids,
        date_from=search_filter.date_from,
        date_to=search_filter.date_to,
        sort_by=search_filter.sort_by
    )
    
    # Get all categories for filters
    categories = Categorie.objects.all()
    
    # Pagination
    paginator = Paginator(articles, 6)  # 6 articles per page
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get popular authors (top 5 by article count)
    from django.db.models import Count
    popular_authors = User.objects.annotate(
        article_count=Count('articles', filter=Q(articles__statut='published'))
    ).filter(article_count__gt=0).order_by('-article_count')[:5]
    
    # Get search suggestions if there's a query
    suggestions = []
    if search_filter.query:
        suggestions = SearchEngine.get_search_suggestions(search_filter.query)
        
        # Add search highlighting to articles
        for article in articles:
            article.highlighted_title = SearchEngine.highlight_search_terms(
                article.titre, search_filter.query, max_length=100
            )
            article.highlighted_excerpt = SearchEngine.highlight_search_terms(
                article.extrait or article.contenu, search_filter.query, max_length=200
            )
    
    # Get trending articles
    trending_articles = SearchEngine.get_trending_articles()
    
    context = {
        'articles': articles,
        'categories': categories,
        'search_form': search_form,
        'search_filter': search_filter,
        'popular_authors': popular_authors,
        'suggestions': suggestions,
        'trending_articles': trending_articles,
        'search_query': search_filter.query,  # For backward compatibility
        'categorie_selectionnee': search_filter.category_id,  # For backward compatibility
        'sort_by': search_filter.sort_by,
    }
    return render(request, 'blog/home.html', context)

@user_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = article.comments.filter(statut='approved').order_by('date_creation')
    
    # Track article view
    article.increment_views()
    
    # Track analytics
    if hasattr(request, 'session'):
        from analytics.models import ArticleView
        ArticleView.objects.create(
            article=article,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            session_key=request.session.session_key or ''
        )
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            if request.user.is_authenticated:
                comment.author = request.user
                comment.nom = request.user.get_full_name() or request.user.username
                comment.email = request.user.email
            comment.save()
            messages.success(request, 'Commentaire ajouté avec succès!')
            return redirect('article_detail', article_id=article.id)
    else:
        comment_form = CommentForm()
    
    # Get similar articles
    similar_articles = article.get_similar_articles()
    
    # Check if user has liked or bookmarked this article
    user_liked = False
    user_bookmarked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, article=article).exists()
        user_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()
    
    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'similar_articles': similar_articles,
        'reading_time': article.get_reading_time(),
        'user_liked': user_liked,
        'user_bookmarked': user_bookmarked,
    }
    return render(request, 'blog/article_detail.html', context)

@superadmin_required
def ajouter_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.save()
            messages.success(request, 'Article ajouté avec succès!')
            return redirect('home')
    else:
        form = ArticleForm()
    
    return render(request, 'blog/ajouter_article.html', {'form': form})

@superadmin_required
def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie ajoutée avec succès!')
            return redirect('categories')
    else:
        form = CategorieForm()
    
    return render(request, 'blog/ajouter_categorie.html', {'form': form})

@user_required
def categories(request):
    categories = Categorie.objects.all()
    return render(request, 'blog/categories.html', {'categories': categories})

@superadmin_required
def modifier_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, f'Catégorie "{categorie.nom}" modifiée avec succès!')
            return redirect('categories')
    else:
        form = CategorieForm(instance=categorie)
    
    context = {
        'form': form,
        'categorie': categorie,
        'mode': 'modification'
    }
    return render(request, 'blog/ajouter_categorie.html', context)

@superadmin_required
def supprimer_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    if request.method == 'POST':
        # Check if category has articles
        if categorie.articles.exists():
            messages.error(request, _('Impossible de supprimer la catégorie "{}" car elle contient des articles.').format(categorie.nom))
        else:
            nom_categorie = categorie.nom
            categorie.delete()
            messages.success(request, f'Catégorie "{nom_categorie}" supprimée avec succès!')
        return redirect('categories')
    
    context = {
        'categorie': categorie,
        'articles_count': categorie.articles.count()
    }
    return render(request, 'blog/supprimer_categorie.html', context)

@superadmin_required
def modifier_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f'Article "{article.titre}" modifié avec succès!')
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
        'mode': 'modification'
    }
    return render(request, 'blog/ajouter_article.html', context)

@superadmin_required
def supprimer_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        titre_article = article.titre
        article.delete()
        messages.success(request, f'Article "{titre_article}" supprimé avec succès!')
        return redirect('home')
    
    context = {
        'article': article,
        'comments_count': article.comments.count()
    }
    return render(request, 'blog/supprimer_article.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {username}! You are now logged in.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    return redirect('home')

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse_lazy

class HomeRedirectView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse_lazy('home')
        else:
            return reverse_lazy('login')

@login_required
@require_POST
def toggle_like(request, article_id):
    """Toggle like status for an article (AJAX endpoint)"""
    try:
        article = get_object_or_404(Article, id=article_id)
        like, created = Like.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if not created:
            # Like already exists, so remove it
            like.delete()
            liked = False
            # Decrease the like count
            article.likes_count = max(0, article.likes_count - 1)
        else:
            liked = True
            # Increase the like count
            article.likes_count += 1
        
        article.save(update_fields=['likes_count'])
        
        return JsonResponse({
            'liked': liked,
            'likes_count': article.likes_count,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def toggle_bookmark(request, article_id):
    """Toggle bookmark status for an article (AJAX endpoint)"""
    try:
        article = get_object_or_404(Article, id=article_id)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if not created:
            # Bookmark already exists, so remove it
            bookmark.delete()
            bookmarked = False
        else:
            bookmarked = True
        
        return JsonResponse({
            'bookmarked': bookmarked,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_required
def user_profile(request, username):
    """Display user profile with their articles and statistics"""
    profile_user = get_object_or_404(User, username=username)
    
    # Get user's published articles
    user_articles = Article.objects.filter(
        auteur=profile_user,
        statut='published'
    ).order_by('-date_creation')
    
    # Pagination for user articles
    paginator = Paginator(user_articles, 6)
    page = request.GET.get('page')
    try:
        user_articles = paginator.page(page)
    except PageNotAnInteger:
        user_articles = paginator.page(1)
    except EmptyPage:
        user_articles = paginator.page(paginator.num_pages)
    
    # Calculate statistics
    total_articles = Article.objects.filter(auteur=profile_user, statut='published').count()
    total_views = sum(article.vues for article in Article.objects.filter(auteur=profile_user, statut='published'))
    total_likes = sum(article.likes_count for article in Article.objects.filter(auteur=profile_user, statut='published'))
    
    # Get bookmarked articles if viewing own profile
    bookmarked_articles = []
    if request.user == profile_user:
        bookmarked_articles = Article.objects.filter(
            bookmarks__user=request.user,
            statut='published'
        ).order_by('-bookmarks__date_creation')[:5]
    
    context = {
        'profile_user': profile_user,
        'user_articles': user_articles,
        'total_articles': total_articles,
        'total_views': total_views,
        'total_likes': total_likes,
        'bookmarked_articles': bookmarked_articles,
        'is_own_profile': request.user == profile_user,
    }
    return render(request, 'blog/user_profile.html', context)

@user_required
def dashboard(request):
    """Author dashboard with detailed statistics"""
    if not request.user.profile.is_author():
        messages.error(request, _("Vous n'avez pas les permissions pour accéder au dashboard auteur."))
        return redirect('home')
    
    # Get user's articles
    user_articles = Article.objects.filter(auteur=request.user).order_by('-date_creation')
    draft_articles = user_articles.filter(statut='draft')
    published_articles = user_articles.filter(statut='published')
    
    # Pagination for articles
    paginator = Paginator(user_articles, 10)
    page = request.GET.get('page')
    try:
        user_articles = paginator.page(page)
    except PageNotAnInteger:
        user_articles = paginator.page(1)
    except EmptyPage:
        user_articles = paginator.page(paginator.num_pages)
    
    # Recent comments on user's articles
    recent_comments = Comment.objects.filter(
        article__auteur=request.user,
        statut='approved'
    ).order_by('-date_creation')[:10]
    
    # Statistics
    total_views = sum(article.vues for article in published_articles)
    total_likes = sum(article.likes_count for article in published_articles)
    
    context = {
        'user_articles': user_articles,
        'draft_count': draft_articles.count(),
        'published_count': published_articles.count(),
        'recent_comments': recent_comments,
        'total_views': total_views,
        'total_likes': total_likes,
    }
    return render(request, 'blog/dashboard.html', context)

@login_required
@require_POST
def toggle_article_status(request, article_id):
    """Toggle article status between draft and published"""
    try:
        article = get_object_or_404(Article, id=article_id)
        
        # Check if user is the author or has permission
        if article.auteur != request.user and not request.user.profile.is_editor():
            return JsonResponse({
                'status': 'error',
                'message': 'Permission denied'
            }, status=403)
        
        # Toggle status
        if article.statut == 'draft':
            article.statut = 'published'
        elif article.statut == 'published':
            article.statut = 'draft'
        # For archived articles, default to published
        elif article.statut == 'archived':
            article.statut = 'published'
        
        article.save(update_fields=['statut'])
        
        return JsonResponse({
            'status': 'success',
            'new_status': article.statut,
            'status_display': article.get_statut_display()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def search_suggestions(request):
    """API endpoint for search autocomplete suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    try:
        suggestions = SearchEngine.get_search_suggestions(query, limit=8)
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        return JsonResponse({'suggestions': [], 'error': str(e)})

def search_results(request):
    """Enhanced search results page with highlighting"""
    search_filter = SearchFilter(request)
    search_form = AdvancedSearchForm(request.GET)
    
    if not search_filter.query:
        return redirect('home')
    
    # Get search results
    articles = SearchEngine.search_articles(
        query=search_filter.query,
        category_id=search_filter.category_id,
        author_id=search_filter.author_id,
        tag_ids=search_filter.tag_ids,
        date_from=search_filter.date_from,
        date_to=search_filter.date_to,
        sort_by=search_filter.sort_by
    )
    
    # Add highlighted excerpts to articles
    for article in articles:
        article.highlighted_title = SearchEngine.highlight_search_terms(
            article.titre, search_filter.query, max_length=100
        )
        article.highlighted_excerpt = SearchEngine.highlight_search_terms(
            article.extrait or article.contenu, search_filter.query, max_length=300
        )
    
    # Pagination
    paginator = Paginator(articles, 10)  # 10 results per page
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Get suggestions if no results
    suggestions = []
    if not articles.object_list:
        suggestions = SearchEngine.get_search_suggestions(search_filter.query)
    
    context = {
        'articles': articles,
        'search_form': search_form,
        'search_filter': search_filter,
        'suggestions': suggestions,
        'total_results': paginator.count,
    }
    
    return render(request, 'blog/search_results.html', context)

@superadmin_required
def analytics_dashboard(request):
    """Analytics dashboard for comprehensive blog statistics"""
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    from .models import Tag
    
    # Basic stats
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(statut='published').count()
    draft_articles = Article.objects.filter(statut='draft').count()
    total_comments = Comment.objects.filter(statut='approved').count()
    total_users = User.objects.count()
    
    # View and engagement stats
    total_views = sum(article.vues for article in Article.objects.all())
    total_likes = Like.objects.count()
    total_bookmarks = Bookmark.objects.count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_articles = Article.objects.filter(date_creation__gte=thirty_days_ago).count()
    recent_comments = Comment.objects.filter(date_creation__gte=thirty_days_ago).count()
    
    # Top performing content
    top_articles = Article.objects.filter(statut='published').order_by('-vues')[:10]
    top_categories = Categorie.objects.annotate(
        article_count=Count('articles', filter=Q(articles__statut='published')),
        total_views=Sum('articles__vues'),
        total_likes=Count('articles__likes')
    ).filter(article_count__gt=0).order_by('-total_views')[:5]
    
    # Trending tags
    trending_tags = Tag.get_trending_tags()[:10]
    
    # Author performance
    top_authors = User.objects.annotate(
        article_count=Count('articles', filter=Q(articles__statut='published')),
        total_views=Sum('articles__vues'),
        total_likes=Count('articles__likes'),
        avg_views=Avg('articles__vues')
    ).filter(article_count__gt=0).order_by('-total_views')[:5]
    
    # Monthly article trends (last 12 months)
    from django.db.models.functions import TruncMonth
    monthly_data = Article.objects.filter(
        date_creation__gte=datetime.now().date() - timedelta(days=365)
    ).annotate(month=TruncMonth('date_creation')).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Engagement rates
    avg_comments_per_article = Comment.objects.filter(
        statut='approved'
    ).count() / max(published_articles, 1)
    
    avg_likes_per_article = Like.objects.count() / max(published_articles, 1)
    
    # Recent activity timeline
    recent_activity = []
    
    # Recent articles
    for article in Article.objects.order_by('-date_creation')[:5]:
        recent_activity.append({
            'type': 'article',
            'title': article.titre,
            'author': article.auteur.username,
            'date': article.date_creation,
            'url': f'/article/{article.id}/'
        })
    
    # Recent comments
    for comment in Comment.objects.filter(statut='approved').order_by('-date_creation')[:5]:
        recent_activity.append({
            'type': 'comment',
            'title': f'Comment on "{comment.article.titre}"',
            'author': comment.nom,
            'date': comment.date_creation,
            'url': f'/article/{comment.article.id}/'
        })
    
    # Sort recent activity by date
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]
    
    context = {
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'total_comments': total_comments,
        'total_users': total_users,
        'total_views': total_views,
        'total_likes': total_likes,
        'total_bookmarks': total_bookmarks,
        'recent_articles': recent_articles,
        'recent_comments': recent_comments,
        'top_articles': top_articles,
        'top_categories': top_categories,
        'trending_tags': trending_tags,
        'top_authors': top_authors,
        'monthly_data': list(monthly_data),
        'avg_comments_per_article': round(avg_comments_per_article, 2),
        'avg_likes_per_article': round(avg_likes_per_article, 2),
        'recent_activity': recent_activity,
    }
    
    return render(request, 'blog/analytics_dashboard.html', context)

@login_required
def comment_moderation(request):
    """Comment moderation interface for editors and admins"""
    # Check if user has moderation permissions
    if not (hasattr(request.user, 'profile') and request.user.profile.is_editor()):
        messages.error(request, 'You do not have permission to moderate comments.')
        return redirect('home')
    
    # Get all comments with filters
    comments = Comment.objects.all().order_by('-date_creation')
    
    # Apply filters
    status_filter = request.GET.get('status')
    article_filter = request.GET.get('article')
    search_query = request.GET.get('search')
    
    if status_filter:
        comments = comments.filter(statut=status_filter)
    
    if article_filter:
        comments = comments.filter(article__id=article_filter)
    
    if search_query:
        comments = comments.filter(
            Q(contenu__icontains=search_query) |
            Q(nom__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(article__titre__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(comments, 20)  # Show 20 comments per page
    page = request.GET.get('page')
    
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    
    # Get statistics
    all_comments = Comment.objects.all()
    pending_count = all_comments.filter(statut='pending').count()
    approved_count = all_comments.filter(statut='approved').count()
    rejected_count = all_comments.filter(statut='rejected').count()
    total_count = all_comments.count()
    
    # Get all articles for filter dropdown
    all_articles = Article.objects.filter(statut='published').order_by('titre')
    
    context = {
        'comments': comments,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
        'all_articles': all_articles,
    }
    
    return render(request, 'blog/comment_moderation.html', context)

@login_required
@require_POST
def moderate_comment_individual(request, comment_id):
    """Moderate individual comment via AJAX"""
    # Check permissions
    if not (hasattr(request.user, 'profile') and request.user.profile.is_editor()):
        return JsonResponse({
            'status': 'error',
            'message': 'Permission denied'
        }, status=403)
    
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'approve':
            comment.approve(request.user)
            message = f'Comment from {comment.nom} approved successfully.'
        elif action == 'reject':
            comment.reject(request.user)
            message = f'Comment from {comment.nom} rejected successfully.'
        elif action == 'delete':
            author_name = comment.nom
            comment.delete()
            message = f'Comment from {author_name} deleted successfully.'
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid action'
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'message': message
        })
        
    except Comment.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Comment not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def bulk_moderate_comments(request):
    """Bulk moderation of comments"""
    # Check permissions
    if not (hasattr(request.user, 'profile') and request.user.profile.is_editor()):
        messages.error(request, 'You do not have permission to moderate comments.')
        return redirect('comment_moderation')
    
    comment_ids = request.POST.getlist('comment_ids')
    action = request.POST.get('action')
    
    if not comment_ids:
        messages.warning(request, 'No comments selected.')
        return redirect('comment_moderation')
    
    try:
        comments = Comment.objects.filter(id__in=comment_ids)
        count = comments.count()
        
        if action == 'approve':
            for comment in comments:
                comment.approve(request.user)
            messages.success(request, f'{count} comment(s) approved successfully.')
            
        elif action == 'reject':
            for comment in comments:
                comment.reject(request.user)
            messages.success(request, f'{count} comment(s) rejected successfully.')
            
        elif action == 'delete':
            comments.delete()
            messages.success(request, f'{count} comment(s) deleted successfully.')
            
        else:
            messages.error(request, 'Invalid action.')
            
    except Exception as e:
        messages.error(request, f'Error processing comments: {str(e)}')
    
    return redirect('comment_moderation')

@user_required
def ai_article_generator(request):
    """AI-powered article generator using Gemini API"""
    if not (request.user.profile.is_superadmin or request.user.profile.is_author()):
        messages.error(request, _("Vous n'avez pas les permissions pour générer des articles."))
        return redirect('home')
    
    generated_article = None
    categories = Categorie.objects.all()
    
    if request.method == 'POST':
        if 'generate' in request.POST:
            # Generate article with Gemini
            subject = request.POST.get('subject', '').strip()
            if subject:
                try:
                    # Configure Gemini API
                    gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
                    if not gemini_api_key:
                        messages.error(request, _("Clé API Gemini non configurée. Veuillez contacter l'administrateur."))
                        return render(request, 'blog/ai_article_generator.html', {
                            'categories': categories
                        })
                    
                    genai.configure(api_key=gemini_api_key)
                    # Use the updated model name
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    # Generate article content with improved prompt
                    prompt = f"""
                    Écris un article de blog complet et engageant sur le sujet: "{subject}"
                    
                    L'article doit inclure:
                    - Un titre accrocheur
                    - Une introduction captivante (2-3 paragraphes)
                    - Un contenu bien structuré avec des sous-titres
                    - Une conclusion pertinente
                    - Un extrait/résumé de 150-200 mots pour la description
                    
                    Format de réponse OBLIGATOIRE (respecte exactement ce format):
                    TITRE: [titre de l'article]
                    EXTRAIT: [extrait/résumé en 150-200 mots]
                    CONTENU: [contenu complet de l'article avec des paragraphes bien structurés]
                    
                    Assure-toi que l'article soit informatif, bien écrit et adapté à un blog professionnel.
                    Utilise des paragraphes courts et aérés pour une meilleure lisibilité.
                    """
                    
                    # Add safety settings
                    safety_settings = [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH", 
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                    
                    response = model.generate_content(
                        prompt,
                        safety_settings=safety_settings,
                        generation_config={
                            "temperature": 0.7,
                            "top_p": 0.8,
                            "top_k": 40,
                            "max_output_tokens": 2048,
                        }
                    )
                    
                    if response and response.text:
                        # Parse the response
                        content = response.text.strip()
                        
                        # Initialize variables
                        title = ""
                        excerpt = ""
                        article_content = ""
                        
                        # Try to parse the structured response
                        lines = content.split('\n')
                        current_section = None
                        excerpt_lines = []
                        content_lines = []
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            if line.startswith('TITRE:'):
                                title = line.replace('TITRE:', '').strip()
                                current_section = 'title'
                            elif line.startswith('EXTRAIT:'):
                                excerpt_text = line.replace('EXTRAIT:', '').strip()
                                if excerpt_text:
                                    excerpt_lines.append(excerpt_text)
                                current_section = 'excerpt'
                            elif line.startswith('CONTENU:'):
                                content_text = line.replace('CONTENU:', '').strip()
                                if content_text:
                                    content_lines.append(content_text)
                                current_section = 'content'
                            elif current_section == 'excerpt':
                                excerpt_lines.append(line)
                            elif current_section == 'content':
                                content_lines.append(line)
                        
                        # Join the lines
                        excerpt = ' '.join(excerpt_lines).strip()
                        article_content = '\n\n'.join(content_lines).strip()
                        
                        # Fallback parsing if structured format fails
                        if not title or not article_content:
                            # Try to extract title from first line or generate one
                            first_lines = content.split('\n')[:10]
                            for line in first_lines:
                                if line.strip() and not line.startswith('#'):
                                    title = line.strip()
                                    break
                            
                            if not title:
                                title = f"Article sur {subject}"
                            
                            # Use the full content if parsing failed
                            if not article_content:
                                article_content = content
                            
                            # Generate excerpt from content if not found
                            if not excerpt:
                                # Remove any markdown headers and get first 200 chars
                                clean_content = content.replace('#', '').replace('**', '')
                                excerpt = clean_content[:200].strip()
                                if len(clean_content) > 200:
                                    excerpt += "..."
                        
                        # Ensure we have minimum content
                        if title and article_content:
                            generated_article = {
                                'title': title,
                                'excerpt': excerpt,
                                'content': article_content,
                                'subject': subject
                            }
                            messages.success(request, _("Article généré avec succès!"))
                        else:
                            messages.error(request, _("Erreur lors du parsing de la réponse. Contenu généré incomplet."))
                    else:
                        messages.error(request, _("Aucune réponse reçue de l'API Gemini."))
                        
                except Exception as e:
                    error_msg = str(e)
                    if "API_KEY" in error_msg.upper():
                        messages.error(request, _("Clé API Gemini invalide. Veuillez vérifier la configuration."))
                    elif "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
                        messages.error(request, _("Quota API dépassé. Veuillez réessayer plus tard."))
                    elif "SAFETY" in error_msg.upper():
                        messages.error(request, _("Le contenu a été bloqué par les filtres de sécurité. Essayez avec un sujet différent."))
                    else:
                        messages.error(request, _("Erreur API Gemini: {}").format(error_msg))
                    print(f"Gemini API Error: {e}")  # For debugging
            else:
                messages.error(request, _("Veuillez saisir un sujet pour l'article."))
        
        elif 'publish' in request.POST:
            # Publish the generated article
            title = request.POST.get('title', '').strip()
            excerpt = request.POST.get('excerpt', '').strip()
            content = request.POST.get('content', '').strip()
            category_id = request.POST.get('category')
            
            # Debug: Print received data
            print(f"DEBUG - Publish data: request.POST={request.POST}")
            print(f"DEBUG - Parsed data: title='{title}', excerpt='{excerpt[:50]}...', content='{content[:50]}...', category_id='{category_id}'")
            
            if not title:
                messages.error(request, _("Le titre est requis pour publier l'article."))
                print("DEBUG - Validation error: Title is missing.")
            elif not content:
                messages.error(request, _("Le contenu est requis pour publier l'article."))
                print("DEBUG - Validation error: Content is missing.")
            else:
                try:
                    print("DEBUG - Attempting to create Article object...")
                    # Create the article with all required fields
                    article = Article.objects.create(
                        titre=title,
                        contenu=content,
                        extrait=excerpt if excerpt else '',
                        auteur=request.user,
                        statut='published'
                    )
                    print(f"DEBUG - Article object created: ID={article.id}, Title='{article.titre}'")
                    
                    # Set category if provided
                    if category_id:
                        try:
                            print(f"DEBUG - Attempting to get category with ID: {category_id}")
                            category = Categorie.objects.get(id=category_id)
                            article.categorie = category
                            article.save(update_fields=['categorie'])
                            print(f"DEBUG - Category '{category.nom}' set for article.")
                        except Categorie.DoesNotExist:
                            messages.warning(request, _("Catégorie sélectionnée non trouvée."))
                            print(f"DEBUG - Category DoesNotExist for ID: {category_id}")
                        except ValueError as ve:
                            messages.error(request, _("ID de catégorie invalide: {}").format(str(ve)))
                            print(f"DEBUG - ValueError for category ID: {category_id}, Error: {ve}")
                    else:
                        print("DEBUG - No category ID provided.")
                    
                    messages.success(request, _("Article '{}' publié avec succès!").format(title))
                    print(f"DEBUG - Article '{title}' published successfully. Redirecting to article_detail.")
                    return redirect('article_detail', article_id=article.id)
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"ERROR creating article: {error_details}")
                    messages.error(request, _("Erreur lors de la publication: {}").format(str(e)))
    
    context = {
        'generated_article': generated_article,
        'categories': categories,
    }
    
    return render(request, 'blog/ai_article_generator.html', context)