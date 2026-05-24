"""
Communication App URLs - Announcements and Notifications
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for ViewSets
router = DefaultRouter()
# router.register(r'announcements', AnnouncementViewSet)
# router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add additional URL patterns here
]
