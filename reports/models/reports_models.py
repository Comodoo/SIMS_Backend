"""
Reports Models - System Reports and Audit Logs
"""
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    """Generated system reports for auditing and analytics."""
    REPORT_TYPES = [
        ('attendance', 'Attendance Report'),
        ('grades', 'Grades Report'),
        ('enrollment', 'Enrollment Report'),
        ('staff_performance', 'Staff Performance Report'),
        ('student_performance', 'Student Performance Report'),
        ('financial', 'Financial Report'),
        ('attendance_summary', 'Attendance Summary'),
        ('leave_summary', 'Leave Summary'),
        ('course_statistics', 'Course Statistics'),
        ('user_activity', 'User Activity Report'),
        ('custom', 'Custom Report'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF Document'),
        ('excel', 'Excel Spreadsheet'),
        ('csv', 'CSV File'),
        ('json', 'JSON Data'),
    ]
    
    report_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='pdf')
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    # Report parameters stored as JSON
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Report generation parameters (date range, filters, etc.)"
    )
    # Report data
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Report data in JSON format"
    )
    file_url = models.URLField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    # Timestamps
    generated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['generated_by']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
    
    @property
    def is_expired(self):
        """Check if report has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_completed(self, file_url=None, file_size=None):
        """Mark report as completed."""
        self.status = 'completed'
        self.generated_at = timezone.now()
        if file_url:
            self.file_url = file_url
        if file_size:
            self.file_size = file_size
        self.save()


class ReportSchedule(models.Model):
    """Scheduled reports for automatic generation."""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    schedule_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=Report.REPORT_TYPES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    # Schedule parameters
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Report parameters for scheduled generation"
    )
    # Recipients
    recipients = models.ManyToManyField(
        User,
        related_name='scheduled_reports',
        blank=True
    )
    # Email settings
    email_enabled = models.BooleanField(default=True)
    email_subject = models.CharField(max_length=200, null=True, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_schedules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_schedules'
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
        indexes = [
            models.Index(fields=['frequency']),
            models.Index(fields=['is_active']),
            models.Index(fields=['next_run']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


# AuditLog is now in core.models.core_models to avoid conflicts


class SystemMetric(models.Model):
    """System performance and usage metrics."""
    metric_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50)
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'system_metrics'
        verbose_name = 'System Metric'
        verbose_name_plural = 'System Metrics'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit or ''}"
