"""
Communication GraphQL Queries (Strawberry)
"""

import strawberry
from typing import Optional, List
from django.db import models
from django.utils import timezone
from communication.models.communication_models import Announcement, AnnouncementReadReceipt, Notification
from communication.schema.communication_schema import AnnouncementType, NotificationType, AnnouncementReadReceiptType


@strawberry.type
class CommunicationQuery:
    """GraphQL queries for Communication module"""
    
    @strawberry.field
    def announcements(
        self,
        target_role: Optional[str] = None,
        priority: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_current: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnnouncementType]:
        """Query announcements with filters"""
        queryset = Announcement.objects.all()
        if target_role:
            queryset = queryset.filter(target_role=target_role)
        if priority:
            queryset = queryset.filter(priority=priority)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if is_current is not None:
            if is_current:
                queryset = queryset.filter(
                    is_active=True,
                    publish_at__lte=timezone.now()
                ).filter(
                    models.Q(expire_at__isnull=True) | models.Q(expire_at__gt=timezone.now())
                )
        return [AnnouncementType.from_model(announcement) for announcement in queryset[offset:offset+limit]]
    
    @strawberry.field
    def announcement(self, id: strawberry.ID) -> Optional[AnnouncementType]:
        """Get announcement by ID"""
        try:
            instance = Announcement.objects.get(ann_id=id)
            return AnnouncementType.from_model(instance)
        except Announcement.DoesNotExist:
            return None
    
    @strawberry.field
    def notifications(
        self,
        recipient_id: Optional[strawberry.ID] = None,
        notification_type: Optional[str] = None,
        is_read: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[NotificationType]:
        """Query notifications with filters"""
        queryset = Notification.objects.all()
        if recipient_id:
            queryset = queryset.filter(recipient_id=recipient_id)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        return [NotificationType.from_model(notification) for notification in queryset[offset:offset+limit]]
    
    @strawberry.field
    def notification(self, id: strawberry.ID) -> Optional[NotificationType]:
        """Get notification by ID"""
        try:
            instance = Notification.objects.get(notification_id=id)
            return NotificationType.from_model(instance)
        except Notification.DoesNotExist:
            return None
    
    @strawberry.field
    def unread_notifications_count(self, recipient_id: strawberry.ID) -> int:
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(
            recipient_id=recipient_id,
            is_read=False
        ).count()
    
    @strawberry.field
    def announcement_read_receipts(
        self,
        announcement_id: strawberry.ID,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnnouncementReadReceiptType]:
        """Query announcement read receipts"""
        queryset = AnnouncementReadReceipt.objects.filter(announcement_id=announcement_id)
        return [AnnouncementReadReceiptType.from_model(receipt) for receipt in queryset[offset:offset+limit]]
