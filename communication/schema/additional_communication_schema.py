"""
Additional Communication GraphQL Schema Types - Updated Notifications
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from communication.models.communication_models import Notification


@strawberry.type
class NotificationType:
    """GraphQL type for Notification (updated for 21-table schema)"""
    id: strawberry.ID
    recipient_id: Optional[strawberry.ID]
    recipient_phone: Optional[str]
    type: str
    subject: Optional[str]
    body: str
    status: str
    sent_at: Optional[str]
    created_at: str
    related_table: Optional[str]
    related_id: Optional[strawberry.ID]
    
    @classmethod
    def from_model(cls, notification: Notification) -> 'NotificationType':
        return cls(
            id=str(notification.notif_id),
            recipient_id=str(notification.recipient.user_id) if notification.recipient else None,
            recipient_phone=notification.recipient_phone,
            type=notification.type,
            subject=notification.subject,
            body=notification.body,
            status=notification.status,
            sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
            created_at=notification.created_at.isoformat(),
            related_table=notification.related_table,
            related_id=str(notification.related_id) if notification.related_id else None,
        )


# Input Types
@strawberry.input
class NotificationInput:
    """Input for creating Notification"""
    recipient_id: Optional[strawberry.ID] = None
    recipient_phone: Optional[str] = None
    type: str
    subject: Optional[str] = None
    body: str
    related_table: Optional[str] = None
    related_id: Optional[strawberry.ID] = None
