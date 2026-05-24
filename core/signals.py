"""
Django Signals for Real-time Updates and Automated Actions
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import Attendance, StudentAttendance


@receiver(post_save, sender=Attendance)
def broadcast_attendance_update(sender, instance, created, **kwargs):
    """
    Broadcast attendance update to WebSocket when staff clocks in/out.
    """
    if created:
        channel_layer = get_channel_layer()
        
        # Prepare event data
        event_data = {
            'type': 'attendance_event',
            'event_type': 'clock_in' if instance.status == 'in' else 'clock_out',
            'user_id': str(instance.user_id),
            'staff_name': instance.staff.full_name if instance.staff else instance.user.username,
            'timestamp': instance.timestamp.isoformat(),
            'is_late': instance.is_late,
            'department': instance.staff.department if instance.staff else None,
            'location': instance.location,
        }
        
        # Get current stats
        from datetime import date
        today = date.today()
        from core.models import Staff
        
        total_staff = Staff.objects.filter(is_active=True).count()
        today_attendance = Attendance.objects.filter(
            timestamp__date=today,
            status='in'
        )
        present_count = today_attendance.values('staff').distinct().count()
        late_count = today_attendance.filter(is_late=True).values('staff').distinct().count()
        
        event_data['stats'] = {
            'total_staff': total_staff,
            'present': present_count,
            'absent': total_staff - present_count,
            'late': late_count,
        }
        
        # Broadcast to attendance group
        async_to_sync(channel_layer.group_send)(
            'attendance_updates',
            event_data
        )
        
        # Also broadcast to dashboard group for admin updates
        async_to_sync(channel_layer.group_send)(
            'admin_dashboard',
            {
                'type': 'dashboard_update',
                'update_type': 'attendance',
                'data': event_data
            }
        )


@receiver(post_save, sender=StudentAttendance)
def notify_on_absence(sender, instance, created, **kwargs):
    """
    Trigger parent notification when student is marked absent.
    """
    if created and instance.status == 'absent' and not instance.notified_parent:
        # This is handled in the model's save method,
        # but we can add additional logic here if needed
        pass


def send_notification_to_user(user_id, notification_data):
    """
    Send real-time notification to a specific user.
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}_notifications",
        {
            'type': 'notification_event',
            **notification_data
        }
    )
