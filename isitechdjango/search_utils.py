"""
Advanced Search Utilities for the Django Blog
Implements intelligent search, relevance ranking, and suggestions
"""
from django.db.models import Q, Count, Value
from django.db.models.functions import Length
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import re
from collections import Counter
from .models import Article, Tag


class SearchEngine:
    """Enhanced search engine with relevance ranking and highlighting"""
    
    @staticmethod
    def search_articles(query, category_id=None, author_id=None, tag_ids=None, 
                       date_from=None, date_to=None, sort_by='relevance'):
        """
        Advanced article search with multiple criteria and fuzzy matching
        """
        if not query.strip():
            articles = Article.objects.filter(statut='published')
        else:
            # Create search vector for full-text search
            search_vector = SearchVector('titre', weight='A') + \
                           SearchVector('extrait', weight='B') + \
                           SearchVector('contenu', weight='C')
            
            # Split query into individual terms for fuzzy matching
            terms = [term.strip() for term in query.split() if term.strip()]
            
            # Build fuzzy search query
            q_objects = Q()
            
            for term in terms:
                # For each term, create fuzzy matches
                term_q = Q()
                
                # Exact matches (highest priority)
                term_q |= Q(titre__icontains=term)
                term_q |= Q(contenu__icontains=term)
                term_q |= Q(extrait__icontains=term)
                
                # Partial matches for words starting with the term
                if len(term) >= 2:
                    term_q |= Q(titre__iregex=r'\b' + re.escape(term))
                    term_q |= Q(contenu__iregex=r'\b' + re.escape(term))
                    term_q |= Q(extrait__iregex=r'\b' + re.escape(term))
                
                # Add author and tag fuzzy matching
                term_q |= Q(auteur__username__icontains=term)
                term_q |= Q(auteur__first_name__icontains=term)
                term_q |= Q(auteur__last_name__icontains=term)
                term_q |= Q(tags__nom__icontains=term)
                
                q_objects &= term_q
            
            articles = Article.objects.filter(
                q_objects,
                statut='published'
            ).distinct().annotate(
                search=search_vector,
                rank=Value(1)  # Default rank for basic search
            )
            
            # Try PostgreSQL full-text search if available for better ranking
            try:
                search_query = SearchQuery(' & '.join(terms))
                articles = Article.objects.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query)
                ).filter(
                    Q(search=search_query) | q_objects,
                    statut='published'
                ).distinct()
            except Exception:
                # Fall back to basic search if PostgreSQL search not available
                pass
        
        # Apply additional filters
        if category_id:
            articles = articles.filter(categorie_id=category_id)
        
        if author_id:
            articles = articles.filter(auteur_id=author_id)
            
        if tag_ids:
            articles = articles.filter(tags__in=tag_ids).distinct()
            
        if date_from:
            articles = articles.filter(date_creation__gte=date_from)
            
        if date_to:
            articles = articles.filter(date_creation__lte=date_to)
        
        # Apply sorting
        if sort_by == 'relevance' and query.strip():
            articles = articles.order_by('-rank', '-date_creation')
        elif sort_by == 'popular':
            articles = articles.order_by('-vues', '-date_creation')
        elif sort_by == 'recent':
            articles = articles.order_by('-date_creation')
        elif sort_by == 'alphabetic':
            articles = articles.order_by('titre')
        else:
            articles = articles.order_by('-date_creation')
            
        return articles
    
    @staticmethod
    def highlight_search_terms(text, query, max_length=200):
        """
        Highlight search terms in text and create excerpt
        """
        if not query.strip():
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Split query into terms
        terms = [term.strip() for term in query.split() if term.strip()]
        
        # Create patterns that will highlight complete words for partial matches
        patterns = []
        for term in terms:
            # For exact matches, highlight just the term
            patterns.append(f'\\b{re.escape(term)}\\b')
            # For partial matches, highlight the entire word that starts with the term
            if len(term) >= 2:
                patterns.append(f'\\b{re.escape(term)}\\w*\\b')
        
        # Combine patterns with OR (flags will be passed to re.search/re.sub)
        pattern = '|'.join(patterns)
        
        # Find the best excerpt around the first match
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 50)
            end = min(len(text), start + max_length)
            excerpt = text[start:end]
            
            # Adjust to word boundaries to avoid cutting words
            if start > 0:
                space_pos = excerpt.find(' ')
                if space_pos != -1:
                    excerpt = excerpt[space_pos + 1:]
                    start += space_pos + 1
                    
            if end < len(text):
                space_pos = excerpt.rfind(' ')
                if space_pos != -1:
                    excerpt = excerpt[:space_pos]
        else:
            excerpt = text[:max_length]
            start = 0
            end = min(len(text), max_length)
        
        # Highlight complete words that match
        def highlight_match(match_obj):
            return f'<span class="search-highlight">{match_obj.group()}</span>'
        
        highlighted = re.sub(pattern, highlight_match, excerpt, flags=re.IGNORECASE)
        
        prefix = '...' if start > 0 else ''
        suffix = '...' if end < len(text) else ''
        
        return mark_safe(f'{prefix}{highlighted}{suffix}')
    
    @staticmethod
    def get_search_suggestions(query, limit=5):
        """
        Get fuzzy search suggestions based on popular terms and articles
        """
        suggestions = []
        
        if len(query) >= 1:  # Start suggesting from 1 character
            # Clean query for fuzzy matching
            query_clean = query.strip()
            
            # Suggest article titles with fuzzy matching
            article_suggestions = Article.objects.filter(
                Q(titre__icontains=query_clean) |
                Q(titre__iregex=r'\b' + re.escape(query_clean)) if len(query_clean) >= 2 else Q(),
                statut='published'
            ).values_list('titre', flat=True)[:3]
            
            suggestions.extend(article_suggestions)
            
            # Suggest tags with fuzzy matching
            tag_suggestions = Tag.objects.filter(
                Q(nom__icontains=query_clean) |
                Q(nom__iregex=r'\b' + re.escape(query_clean)) if len(query_clean) >= 2 else Q()
            ).values_list('nom', flat=True)[:3]
            
            suggestions.extend([f"#{tag}" for tag in tag_suggestions])
            
            # Add author suggestions
            from django.contrib.auth.models import User
            author_suggestions = User.objects.filter(
                Q(username__icontains=query_clean) |
                Q(first_name__icontains=query_clean) |
                Q(last_name__icontains=query_clean)
            ).values_list('username', flat=True)[:2]
            
            suggestions.extend([f"@{author}" for author in author_suggestions])
        
        return suggestions[:limit]
    
    @staticmethod
    def get_popular_search_terms(limit=10):
        """
        Get popular search terms (would need to implement search logging)
        For now, return popular tags and article words
        """
        # Get popular tags
        popular_tags = Tag.objects.annotate(
            usage_count=Count('articles')
        ).filter(usage_count__gt=0).order_by('-usage_count')[:limit]
        
        return [tag.nom for tag in popular_tags]
    
    @staticmethod
    def get_trending_articles(days=7, limit=5):
        """
        Get trending articles based on recent views
        """
        from datetime import datetime, timedelta
        
        recent_date = datetime.now() - timedelta(days=days)
        
        return Article.objects.filter(
            statut='published',
            date_creation__gte=recent_date
        ).order_by('-vues', '-date_creation')[:limit]


class SearchFilter:
    """Helper class for managing search filters state"""
    
    def __init__(self, request):
        self.request = request
        self.query = request.GET.get('search', '').strip()
        self.category_id = request.GET.get('categorie')
        self.author_id = request.GET.get('author')
        self.tag_ids = request.GET.getlist('tags')
        self.date_from = request.GET.get('date_from')
        self.date_to = request.GET.get('date_to')
        self.sort_by = request.GET.get('sort', 'relevance')
    
    def has_active_filters(self):
        """Check if any filters are active"""
        return bool(self.query or self.category_id or self.author_id or 
                   self.tag_ids or self.date_from or self.date_to)
    
    def get_filter_params(self):
        """Get all filter parameters as dict"""
        params = {}
        if self.query:
            params['search'] = self.query
        if self.category_id:
            params['categorie'] = self.category_id
        if self.author_id:
            params['author'] = self.author_id
        if self.tag_ids:
            params['tags'] = self.tag_ids
        if self.date_from:
            params['date_from'] = self.date_from
        if self.date_to:
            params['date_to'] = self.date_to
        if self.sort_by != 'relevance':
            params['sort'] = self.sort_by
        return params
    
    def get_clear_filter_url(self, exclude_param=None):
        """Get URL with specific filter removed"""
        params = self.get_filter_params()
        if exclude_param and exclude_param in params:
            del params[exclude_param]
        
        if params:
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            return f"?{param_string}"
        return ""
    
    @property
    def clear_search_url(self):
        """Get URL with search filter removed"""
        return self.get_clear_filter_url('search')
    
    @property 
    def clear_category_url(self):
        """Get URL with category filter removed"""
        return self.get_clear_filter_url('categorie')
    
    @property
    def clear_author_url(self):
        """Get URL with author filter removed"""
        return self.get_clear_filter_url('author')
    
    @property
    def clear_all_url(self):
        """Get URL with all filters removed"""
        return ""
    
    @property
    def filter_params_string(self):
        """Get filter parameters as a URL query string"""
        params = self.get_filter_params()
        if not params:
            return ""
        
        # Handle list parameters (tags)
        param_pairs = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    param_pairs.append(f"{key}={v}")
            else:
                param_pairs.append(f"{key}={value}")
        
        return "&".join(param_pairs)
