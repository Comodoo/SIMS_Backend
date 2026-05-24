"""
Communication GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional
from django.utils import timezone
from communication.models.communication_models import Announcement, Notification, AnnouncementReadReceipt
from communication.schema.communication_schema import (
    AnnouncementType, 
    NotificationType, 
    AnnouncementInput, 
    NotificationInput as NotificationInputType, 
    MarkNotificationReadInput, 
    MarkAnnouncementReadInput
)


@strawberry.type
class CommunicationMutationResponse:
    """Response type for communication mutations"""
    success: bool
    message: str


@strawberry.type
class AnnouncementMutationResponse(CommunicationMutationResponse):
    """Response type for announcement mutations"""
    announcement: Optional[AnnouncementType] = None


@strawberry.type
class NotificationMutationResponse(CommunicationMutationResponse):
    """Response type for notification mutations"""
    notification: Optional[NotificationType] = None


def _error_response(message: str) -> CommunicationMutationResponse:
    """Helper for error responses"""
    return CommunicationMutationResponse(success=False, message=message)


@strawberry.type
class CommunicationMutation:
    """GraphQL mutations for Communication module"""
    
    @strawberry.mutation
    def create_announcement(self, input: AnnouncementInput) -> AnnouncementMutationResponse:
        """Create a new announcement"""
        try:
            announcement = Announcement.objects.create(
                title=input.title,
                content=input.content,
                author_id=input.author_id,
                target_role=input.target_role or 'all',
                priority=input.priority or 'medium',
                is_active=input.is_active or True,
                is_pinned=input.is_pinned or False,
                publish_at=input.publish_at or timezone.now(),
                expire_at=input.expire_at
            )
            
            return AnnouncementMutationResponse(
                success=True, 
                message="Announcement created successfully", 
                announcement=AnnouncementType.from_model(announcement)
            )
        except Exception as e:
            return AnnouncementMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_notification(self, input: NotificationInputType) -> NotificationMutationResponse:
        """Create a new notification"""
        try:
            notification = Notification.objects.create(
                recipient_id=input.recipient_id,
                title=input.title,
                message=input.message,
                notification_type=input.notification_type or 'info',
                related_object_type=input.related_object_type,
                related_object_id=input.related_object_id
            )
            
            return NotificationMutationResponse(
                success=True, 
                message="Notification created successfully", 
                notification=NotificationType.from_model(notification)
            )
        except Exception as e:
            return NotificationMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def mark_notification_read(self, input: MarkNotificationReadInput) -> CommunicationMutationResponse:
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(notification_id=input.notification_id)
            notification.mark_as_read()
            
            return CommunicationMutationResponse(success=True, message="Notification marked as read")
        except Notification.DoesNotExist:
            return CommunicationMutationResponse(success=False, message="Notification not found")
        except Exception as e:
            return CommunicationMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def mark_announcement_read(self, input: MarkAnnouncementReadInput) -> CommunicationMutationResponse:
        """Mark announcement as read"""
        try:
            receipt, created = AnnouncementReadReceipt.objects.get_or_create(
                announcement_id=input.announcement_id,
                user_id=input.user_id
            )
            
            return CommunicationMutationResponse(success=True, message="Announcement marked as read")
        except Exception as e:
            return CommunicationMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def mark_all_notifications_read(self, recipient_id: strawberry.ID) -> CommunicationMutationResponse:
        """Mark all notifications as read for a user"""
        try:
            notifications = Notification.objects.filter(
                recipient_id=recipient_id,
                is_read=False
            )
            count = notifications.count()
            notifications.update(is_read=True, read_at=timezone.now())
            
            return CommunicationMutationResponse(
                success=True, 
                message=f"Marked {count} notifications as read"
            )
        except Exception as e:
            return CommunicationMutationResponse(success=False, message=f"Error: {str(e)}")
