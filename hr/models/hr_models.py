"""
HR Models - Leave Management and Staff Attendance
"""
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone


class Leave(models.Model):
    """Staff leave requests and approval tracking."""
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('emergency', 'Emergency Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    leave_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    staff = models.ForeignKey(
        'core.Staff',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPES
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    reason = models.TextField()
    # Approval tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    # Attachments
    attachment_url = models.URLField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaves'
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['staff']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        # Calculate total days
        if self.start_date and self.end_date:
            self.total_days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)
    
    def approve(self, approved_by_user):
        """Approve the leave request."""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
        
        # Send notification
        from communication.tasks import send_leave_approval_notification
        send_leave_approval_notification.delay(str(self.leave_id))
    
    def reject(self, reason, rejected_by_user):
        """Reject the leave request."""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.approved_by = rejected_by_user
        self.approved_at = timezone.now()
        self.save()
        
        # Send notification
        from communication.tasks import send_leave_rejection_notification
        send_leave_rejection_notification.delay(str(self.leave_id))


class LeaveBalance(models.Model):
    """Track staff leave balances."""
    balance_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    staff = models.ForeignKey(
        'core.Staff',
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    year = models.IntegerField()
    # Annual leave
    annual_entitlement = models.IntegerField(default=21)
    annual_used = models.IntegerField(default=0)
    annual_remaining = models.IntegerField(default=21)
    # Sick leave
    sick_entitlement = models.IntegerField(default=10)
    sick_used = models.IntegerField(default=0)
    sick_remaining = models.IntegerField(default=10)
    # Other leave types
    emergency_used = models.IntegerField(default=0)
    unpaid_used = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = ['staff', 'year']
        verbose_name = 'Leave Balance'
        verbose_name_plural = 'Leave Balances'
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.year}"
    
    def update_annual_used(self, days):
        """Update annual leave used."""
        self.annual_used += days
        self.annual_remaining = self.annual_entitlement - self.annual_used
        self.save()
    
    def update_sick_used(self, days):
        """Update sick leave used."""
        self.sick_used += days
        self.sick_remaining = self.sick_entitlement - self.sick_used
        self.save()


class StaffAttendanceSummary(models.Model):
    """Monthly/yearly attendance summaries for staff."""
    summary_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    staff = models.ForeignKey(
        'core.Staff',
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    year = models.IntegerField()
    month = models.IntegerField()
    # Work days calculation
    total_work_days = models.IntegerField()
    days_present = models.IntegerField()
    days_absent = models.IntegerField()
    days_late = models.IntegerField()
    # Time calculations
    total_late_minutes = models.IntegerField(default=0)
    average_late_minutes = models.FloatField(default=0.0)
    # Percentages
    attendance_percentage = models.FloatField()
    punctuality_percentage = models.FloatField()
    # Computed timestamp
    computed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_attendance_summaries'
        unique_together = ['staff', 'year', 'month']
        verbose_name = 'Staff Attendance Summary'
        verbose_name_plural = 'Staff Attendance Summaries'
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.year}/{self.month}"
    
    def calculate_stats(self):
        """Calculate attendance statistics."""
        from core.models import Attendance
        from calendar import monthrange
        
        # Get days in month
        _, days_in_month = monthrange(self.year, self.month)
        
        # Get attendance records for this month
        attendance_records = Attendance.objects.filter(
            staff=self.staff,
            timestamp__year=self.year,
            timestamp__month=self.month,
            status='in'
        )
        
        # Calculate stats
        self.days_present = attendance_records.count()
        self.days_late = attendance_records.filter(is_late=True).count()
        self.total_late_minutes = sum(
            record.late_minutes or 0 
            for record in attendance_records.filter(is_late=True)
        )
        
        # Calculate work days (excluding weekends - simplified)
        self.total_work_days = days_in_month  # Simplified
        self.days_absent = self.total_work_days - self.days_present
        
        # Calculate percentages
        self.attendance_percentage = (
            (self.days_present / self.total_work_days * 100) 
            if self.total_work_days > 0 else 0
        )
        self.punctuality_percentage = (
            ((self.days_present - self.days_late) / self.days_present * 100)
            if self.days_present > 0 else 0
        )
        self.average_late_minutes = (
            self.total_late_minutes / self.days_late 
            if self.days_late > 0 else 0
        )
        
        self.save()
