"""
WebSocket Consumers for Real-time Updates - SIMS Backend
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class AttendanceConsumer(AsyncWebsocketConsumer):
    """
    Real-time attendance updates for admin dashboard.
    Broadcasts clock-in/out events to connected admin clients.
    """
    
    async def connect(self):
        self.room_group_name = 'attendance_updates'
        
        # Join the attendance updates group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to attendance updates'
        }))
    
    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'message': f"Subscribed to {data.get('channel', 'general')}"
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def attendance_event(self, event):
        """
        Handle attendance events from Django signals.
        Broadcast to all connected clients.
        """
        await self.send(text_data=json.dumps({
            'type': 'attendance_update',
            'event': {
                'type': event.get('event_type'),
                'user_id': event.get('user_id'),
                'staff_name': event.get('staff_name'),
                'timestamp': event.get('timestamp'),
                'is_late': event.get('is_late'),
                'department': event.get('department'),
                'location': event.get('location'),
            },
            'stats': event.get('stats', {})
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Real-time notifications for individual users.
    Each user connects to their own notification channel.
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Create a personal notification group for this user
        self.notification_group_name = f"user_{self.user.user_id}_notifications"
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notification count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'unread_count': unread_count,
            'message': 'Connected to notification service'
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for user."""
        from communication.models import Notification
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
    
    async def notification_event(self, event):
        """
        Handle notification events.
        Send new notification to the user.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': {
                'id': event.get('notification_id'),
                'type': event.get('notification_type'),
                'title': event.get('title'),
                'message': event.get('message'),
                'link_url': event.get('link_url'),
                'created_at': event.get('created_at'),
            }
        }))


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    Real-time dashboard updates for admin users.
    Shows live statistics and updates.
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        
        # Only allow admin and staff users
        if self.user.is_anonymous or self.user.role not in ['admin', 'staff']:
            await self.close()
            return
        
        self.dashboard_group = 'admin_dashboard'
        
        await self.channel_layer.group_add(
            self.dashboard_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard stats
        stats = await self.get_dashboard_stats()
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'stats': stats
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'dashboard_group'):
            await self.channel_layer.group_discard(
                self.dashboard_group,
                self.channel_name
            )
    
    @database_sync_to_async
    def get_dashboard_stats(self):
        """Get current dashboard statistics."""
        from datetime import date
        from core.models import Staff, Attendance
        from hr.models import Leave
        
        today = date.today()
        
        total_staff = Staff.objects.filter(is_active=True).count()
        
        # Today's attendance
        today_attendance = Attendance.objects.filter(
            timestamp__date=today,
            status='in'
        )
        present_staff = today_attendance.values('staff').distinct().count()
        late_staff = today_attendance.filter(is_late=True).values('staff').distinct().count()
        
        return {
            'timestamp': timezone.now().isoformat(),
            'total_staff': total_staff,
            'present_staff': present_staff,
            'absent_staff': total_staff - present_staff,
            'late_staff': late_staff,
            'pending_leaves': Leave.objects.filter(status='pending').count(),
        }
    
    async def dashboard_update(self, event):
        """Handle dashboard update events."""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'update_type': event.get('update_type'),
            'data': event.get('data')
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Real-time chat between users.
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join a general chat group
        self.chat_group = 'general_chat'
        
        await self.channel_layer.group_add(
            self.chat_group,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'chat_group'):
            await self.channel_layer.group_discard(
                self.chat_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming chat messages."""
        try:
            data = json.loads(text_data)
            message = data.get('message')
            
            # Broadcast to the group
            await self.channel_layer.group_send(
                self.chat_group,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': str(self.user.user_id),
                    'sender_name': self.user.get_full_name() or self.user.username,
                    'timestamp': str(timezone.now())
                }
            )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        """Handle chat message events."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event.get('message'),
            'sender': event.get('sender'),
            'sender_name': event.get('sender_name'),
            'timestamp': event.get('timestamp')
        }))
