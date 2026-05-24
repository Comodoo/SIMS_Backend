"""
Communication Schema
"""

from .communication_schema import (
    AnnouncementType,
    AnnouncementReadReceiptType,
    NotificationType,
)

from .additional_communication_schema import (
    NotificationType as UpdatedNotificationType,
)

__all__ = [
    'AnnouncementType',
    'AnnouncementReadReceiptType',
    'NotificationType',
]
