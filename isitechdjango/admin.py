from django.contrib import admin
from .models import Article, Comment, Categorie

# Register your models here.
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'couleur', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['nom', 'description']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'categorie', 'date_creation']
    list_filter = ['date_creation', 'auteur', 'categorie']
    search_fields = ['titre', 'contenu']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'article', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['author__username', 'contenu']
