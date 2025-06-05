from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_overview, name='overview'),
    path('articles/', views.article_analytics, name='articles'),
    path('users/', views.user_analytics, name='users'),
    path('api/data/', views.api_analytics_data, name='api_data'),
    path('export/', views.export_analytics, name='export'),
    path('track-reading-time/', views.track_reading_time, name='track_reading_time'),
]
