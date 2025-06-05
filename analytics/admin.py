from django.contrib import admin
from .models import PageView, ArticleView

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['path', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp', 'path']
    search_fields = ['path', 'user__username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'ip_address', 'timestamp', 'reading_time']
    list_filter = ['timestamp', 'article']
    search_fields = ['article__titre', 'user__username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
