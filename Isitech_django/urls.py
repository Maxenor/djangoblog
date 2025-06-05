from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # Add this import
from django.views.i18n import set_language # Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', include('isitechdjango.urls')),
    path('api/v1/', include('isitechdjango.api.urls')),
    path('analytics/', include('analytics.urls')),
    path('i18n/', include('django.conf.urls.i18n')), # Add this line for set_language view
    # Add other internationalized URLs here
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
