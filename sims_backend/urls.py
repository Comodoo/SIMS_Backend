"""
URL Configuration for SIMS Backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sims_backend import graphql_urls

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # GraphQL
    path('', include(graphql_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
