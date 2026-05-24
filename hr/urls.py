"""
HR App URLs - Leave Management and Staff Attendance
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for ViewSets
router = DefaultRouter()
# router.register(r'leaves', LeaveViewSet)
# router.register(r'leave-balances', LeaveBalanceViewSet)
# router.register(r'attendance-summaries', StaffAttendanceSummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add additional URL patterns here
]
