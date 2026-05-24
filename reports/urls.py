"""
Reports App URLs - System Reports and Audit Logs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for ViewSets
router = DefaultRouter()
# router.register(r'reports', ReportViewSet)
# router.register(r'schedules', ReportScheduleViewSet)
# router.register(r'audit-logs', AuditLogViewSet)
# router.register(r'metrics', SystemMetricViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add additional URL patterns here
]
