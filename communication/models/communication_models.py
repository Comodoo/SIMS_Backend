"""
Communication Models - Announcements, AnnouncementReadReceipts, Notifications
Part of 21-Table Schema Implementation
"""
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================================
# 17. ANNOUNCEMENTS TABLE
# ============================================================================

class Announcement(models.Model):
    """
    System-wide announcements for different user roles.
    Updated to match 21-table schema specification.
    """
    TARGET_ROLE_CHOICES = [
        ('admin', 'Administrators'),
        ('staff', 'Staff Members'),
        ('student', 'Students'),
        ('parent', 'Parents/Guardians'),
    ]
    
    ann_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(
        max_length=255,
        help_text="Announcement title"
    )
    content = models.TextField(
        help_text="Announcement content"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_announcements',
        help_text="User who created the announcement"
    )
    target_role = models.CharField(
        max_length=20,
        choices=TARGET_ROLE_CHOICES,
        null=True,
        blank=True,
        help_text="null = everyone"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active status"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiration date"
    )
    
    class Meta:
        db_table = 'announcements'
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title


# ============================================================================
# 18. ANNOUNCEMENT READ RECEIPTS TABLE
# ============================================================================

class AnnouncementReadReceipt(models.Model):
    """
    Tracks which users have read each announcement.
    Enables admins to confirm critical notices have reached everyone.
    """
    receipt_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='read_receipts',
        help_text="The announcement that was read"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='read_announcements',
        help_text="User who read the announcement"
    )
    read_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the announcement was read"
    )
    
    class Meta:
        db_table = 'announcement_read_receipts'
        unique_together = ['announcement', 'user']
        verbose_name = 'Announcement Read Receipt'
        verbose_name_plural = 'Announcement Read Receipts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['read_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"


# ============================================================================
# 19. NOTIFICATIONS TABLE
# ============================================================================

class Notification(models.Model):
    """
    Log of every alert dispatched — in-app toast, email, or SMS.
    Enables retry logic and user notification history.
    Updated to match 21-table schema specification.
    """
    TYPE_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    notif_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="User recipient (null for SMS to parents)"
    )
    recipient_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Phone number for parent SMS alerts"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='in_app',
        help_text="Notification type"
    )
    subject = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Subject for email type"
    )
    body = models.TextField(
        default="",
        help_text="Notification body/content"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Delivery status"
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was sent"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    related_table = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Source context e.g. StudentAttendance"
    )
    related_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="FK to source record"
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        if self.recipient:
            return f"{self.type} to {self.recipient.username}"
        return f"{self.type} to {self.recipient_phone}"
