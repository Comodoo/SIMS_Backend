"""
Academic Structure Models - Departments, Semesters
Part of 21-Table Schema Implementation
"""
import uuid
from django.db import models


# ============================================================================
# 4. DEPARTMENTS TABLE
# ============================================================================

class Department(models.Model):
    """
    Department/Faculty table for institutional management.
    Replaces plain text department strings on Staff and Students tables.
    """
    dept_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Department name"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Department code e.g. CS, BUS"
    )
    hod = models.ForeignKey(
        'core.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        help_text="Head of Department"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Department description"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active status"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    
    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================================================
# 5. SEMESTERS TABLE
# ============================================================================

class Semester(models.Model):
    """
    Academic period definition with open/close dates.
    Replaces raw SEM1-2025 strings across Courses, Enrollments, StudentAttendance.
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    semester_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="e.g. Semester 1 – 2025"
    )
    academic_year = models.CharField(
        max_length=20,
        help_text="e.g. 2024/2025"
    )
    start_date = models.DateField(
        help_text="Semester start date"
    )
    end_date = models.DateField(
        help_text="Semester end date"
    )
    enrollment_open = models.DateField(
        help_text="When students can enroll"
    )
    enrollment_close = models.DateField(
        help_text="Enrollment deadline"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
        help_text="Semester status"
    )
    
    class Meta:
        db_table = 'semesters'
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
        indexes = [
            models.Index(fields=['academic_year']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"
