from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import PageView, ArticleView
from isitechdjango.models import Article, User, Categorie, Tag
from isitechdjango.decorators import superadmin_required


@superadmin_required
def analytics_overview(request):
    """Comprehensive analytics overview for super admins"""
    # Time-based statistics
    now = timezone.now()
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)
    
    # Page view analytics
    total_page_views = PageView.objects.count()
    weekly_page_views = PageView.objects.filter(timestamp__gte=last_week).count()
    monthly_page_views = PageView.objects.filter(timestamp__gte=last_month).count()
    
    # Most popular pages
    popular_pages = PageView.objects.values('path').annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:10]
    
    # Article view analytics
    total_article_views = ArticleView.objects.count()
    average_reading_time = ArticleView.objects.aggregate(
        avg_time=Avg('reading_time')
    )['avg_time'] or 0
    
    # User engagement metrics
    unique_visitors_monthly = PageView.objects.filter(
        timestamp__gte=last_month
    ).values('ip_address').distinct().count()
    
    registered_users_monthly = User.objects.filter(
        date_joined__gte=last_month
    ).count()
    
    # Geographic data (simplified - based on IP patterns)
    geographic_data = PageView.objects.values('ip_address').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Device/Browser analytics (simplified)
    browser_stats = PageView.objects.values('user_agent').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Traffic source analytics
    referrer_stats = PageView.objects.exclude(
        referrer=''
    ).values('referrer').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'total_page_views': total_page_views,
        'weekly_page_views': weekly_page_views,
        'monthly_page_views': monthly_page_views,
        'popular_pages': popular_pages,
        'total_article_views': total_article_views,
        'average_reading_time': round(average_reading_time, 2),
        'unique_visitors_monthly': unique_visitors_monthly,
        'registered_users_monthly': registered_users_monthly,
        'geographic_data': geographic_data,
        'browser_stats': browser_stats,
        'referrer_stats': referrer_stats,
    }
    
    return render(request, 'analytics/overview.html', context)


@superadmin_required
def article_analytics(request):
    """Detailed analytics for individual articles"""
    # Get article performance data
    articles_with_stats = Article.objects.annotate(
        total_views=Count('analytics_views'),
        unique_visitors=Count('analytics_views__ip_address', distinct=True),
        avg_reading_time=Avg('analytics_views__reading_time'),
        total_comments=Count('comments', filter=Q(comments__statut='approved')),
        total_likes=Count('likes')
    ).filter(statut='published').order_by('-total_views')
    
    # Reading time distribution
    reading_time_stats = ArticleView.objects.values('reading_time').annotate(
        count=Count('id')
    ).order_by('reading_time')
    
    # Article performance over time
    article_views_timeline = ArticleView.objects.extra(
        select={
            'date': "DATE(timestamp)"
        }
    ).values('date').annotate(
        views=Count('id')
    ).order_by('date')
    
    context = {
        'articles_with_stats': articles_with_stats[:20],
        'reading_time_stats': reading_time_stats,
        'article_views_timeline': article_views_timeline,
    }
    
    return render(request, 'analytics/article_analytics.html', context)


@superadmin_required
def user_analytics(request):
    """User behavior and engagement analytics"""
    # User engagement metrics
    active_users_daily = PageView.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=1),
        user__isnull=False
    ).values('user').distinct().count()
    
    active_users_weekly = PageView.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=7),
        user__isnull=False
    ).values('user').distinct().count()
    
    active_users_monthly = PageView.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=30),
        user__isnull=False
    ).values('user').distinct().count()
    
    # User session analytics
    session_stats = PageView.objects.values('session_key').annotate(
        page_count=Count('id'),
        duration=Count('timestamp')  # Simplified duration calculation
    ).order_by('-page_count')[:20]
    
    # Most active users
    most_active_users = PageView.objects.filter(
        user__isnull=False
    ).values('user__username', 'user__first_name', 'user__last_name').annotate(
        page_views=Count('id')
    ).order_by('-page_views')[:20]
    
    # User registration trends
    registration_trends = User.objects.extra(
        select={
            'date': "DATE(date_joined)"
        }
    ).values('date').annotate(
        registrations=Count('id')
    ).order_by('date')
    
    context = {
        'active_users_daily': active_users_daily,
        'active_users_weekly': active_users_weekly,
        'active_users_monthly': active_users_monthly,
        'session_stats': session_stats,
        'most_active_users': most_active_users,
        'registration_trends': registration_trends,
    }
    
    return render(request, 'analytics/user_analytics.html', context)


@login_required
def api_analytics_data(request):
    """API endpoint for analytics data (AJAX)"""
    data_type = request.GET.get('type', 'overview')
    
    if data_type == 'page_views_today':
        # Page views for today by hour
        today = timezone.now().date()
        page_views = PageView.objects.filter(
            timestamp__date=today
        ).extra(
            select={
                'hour': "EXTRACT(hour FROM timestamp)"
            }
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        return JsonResponse({
            'labels': [f"{int(pv['hour'])}:00" for pv in page_views],
            'data': [pv['count'] for pv in page_views]
        })
    
    elif data_type == 'top_articles_weekly':
        # Top articles this week
        last_week = timezone.now() - timedelta(days=7)
        top_articles = ArticleView.objects.filter(
            timestamp__gte=last_week
        ).values('article__titre').annotate(
            views=Count('id')
        ).order_by('-views')[:5]
        
        return JsonResponse({
            'labels': [article['article__titre'][:30] for article in top_articles],
            'data': [article['views'] for article in top_articles]
        })
    
    return JsonResponse({'error': 'Invalid data type'})


@superadmin_required
def export_analytics(request):
    """Export analytics data to CSV"""
    import csv
    from django.http import HttpResponse
    
    export_type = request.GET.get('type', 'page_views')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{export_type}_analytics.csv"'
    
    writer = csv.writer(response)
    
    if export_type == 'page_views':
        writer.writerow(['Date', 'Path', 'User', 'IP Address', 'User Agent'])
        for view in PageView.objects.all().order_by('-timestamp'):
            writer.writerow([
                view.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                view.path,
                view.user.username if view.user else 'Anonymous',
                view.ip_address,
                view.user_agent[:100]
            ])
    
    elif export_type == 'article_views':
        writer.writerow(['Date', 'Article', 'User', 'Reading Time', 'IP Address'])
        for view in ArticleView.objects.all().order_by('-timestamp'):
            writer.writerow([
                view.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                view.article.titre,
                view.user.username if view.user else 'Anonymous',
                view.reading_time,
                view.ip_address
            ])
    
    return response


@csrf_exempt
@require_POST
def track_reading_time(request):
    """Track reading time for articles via AJAX"""
    try:
        data = json.loads(request.body)
        article_id = data.get('article_id')
        reading_time = data.get('reading_time', 0)
        
        if article_id and reading_time > 0:
            # Find the most recent article view for this session
            session_key = request.session.session_key or ''
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
            try:
                article_view = ArticleView.objects.filter(
                    article_id=article_id,
                    session_key=session_key,
                    ip_address=ip_address
                ).order_by('-timestamp').first()
                
                if article_view:
                    article_view.reading_time = max(article_view.reading_time, reading_time)
                    article_view.save(update_fields=['reading_time'])
                    
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid data'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
