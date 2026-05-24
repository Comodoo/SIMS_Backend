"""
Communication GraphQL Schema (Strawberry)
Announcements and Notifications
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date
from communication.models.communication_models import Announcement, AnnouncementReadReceipt, Notification
from core.schema.core_schema import UserType


@strawberry.type
class AnnouncementType:
    """GraphQL type for Announcement"""
    id: strawberry.ID
    title: str
    content: str
    author: UserType
    target_role: str
    priority: str
    is_active: bool
    is_pinned: bool
    publish_at: datetime
    expire_at: Optional[datetime] = None
    views_count: int
    is_current: bool
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, instance: Announcement):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.ann_id)),
            title=instance.title,
            content=instance.content,
            author=UserType.from_model(instance.author),
            target_role=instance.target_role,
            priority=instance.priority,
            is_active=instance.is_active,
            is_pinned=instance.is_pinned,
            publish_at=instance.publish_at,
            expire_at=instance.expire_at,
            views_count=instance.views_count,
            is_current=instance.is_current,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class NotificationType:
    """GraphQL type for Notification"""
    id: strawberry.ID
    recipient: UserType
    title: str
    message: str
    notification_type: str
    related_object_type: Optional[str] = None
    related_object_id: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    email_sent: bool
    sms_sent: bool
    created_at: datetime
    
    @classmethod
    def from_model(cls, instance: Notification):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.notification_id)),
            recipient=UserType.from_model(instance.recipient),
            title=instance.title,
            message=instance.message,
            notification_type=instance.notification_type,
            related_object_type=instance.related_object_type,
            related_object_id=str(instance.related_object_id) if instance.related_object_id else None,
            is_read=instance.is_read,
            read_at=instance.read_at,
            email_sent=instance.email_sent,
            sms_sent=instance.sms_sent,
            created_at=instance.created_at,
        )


@strawberry.type
class AnnouncementReadReceiptType:
    """GraphQL type for AnnouncementReadReceipt"""
    id: strawberry.ID
    announcement: AnnouncementType
    user: UserType
    read_at: datetime
    
    @classmethod
    def from_model(cls, instance: AnnouncementReadReceipt):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.receipt_id)),
            announcement=AnnouncementType.from_model(instance.announcement),
            user=UserType.from_model(instance.user),
            read_at=instance.read_at,
        )


# Input Types for Mutations
@strawberry.input
class AnnouncementInput:
    """Input for creating/updating Announcement"""
    title: str
    content: str
    target_role: str = "all"
    priority: str = "medium"
    is_active: bool = True
    is_pinned: bool = False
    publish_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None


@strawberry.input
class NotificationInput:
    """Input for creating Notification"""
    recipient_id: strawberry.ID
    title: str
    message: str
    notification_type: str = "info"
    related_object_type: Optional[str] = None
    related_object_id: Optional[str] = None


@strawberry.input
class MarkNotificationReadInput:
    """Input for marking notification as read"""
    notification_id: strawberry.ID


@strawberry.input
class MarkAnnouncementReadInput:
    """Input for marking announcement as read"""
    announcement_id: strawberry.ID
