"""
WebSocket URL routing configuration for SIMS Backend.
"""
from django.urls import re_path
from sims_backend.consumers import (
    AttendanceConsumer,
    NotificationConsumer,
    DashboardConsumer,
    ChatConsumer
)

websocket_urlpatterns = [
    # Attendance updates (admin dashboard)
    re_path(r'ws/attendance/$', AttendanceConsumer.as_asgi()),
    
    # User notifications (personal)
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    
    # Admin dashboard stats
    re_path(r'ws/dashboard/$', DashboardConsumer.as_asgi()),
    
    # General chat
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
]
