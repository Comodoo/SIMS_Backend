"""
Core Models - Users, Students, Staff, Attendance, RefreshTokens, AuditLog
21-Table Schema Implementation
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import hashlib


# ============================================================================
# 1. USERS TABLE (Extended AbstractUser)
# ============================================================================

class User(AbstractUser):
    """
    Central authentication table with biometric support.
    Extends Django's AbstractUser for authentication.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
        ('student', 'Student'),
        ('parent', 'Parent/Guardian'),
    ]
    
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text="User role for RBAC"
    )
    # Biometric hash stored as encrypted string (not the actual fingerprint image)
    biometric_hash = models.TextField(
        null=True,
        blank=True,
        help_text="Encrypted fingerprint template hash (AES-256)"
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        help_text="Contact phone number"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def generate_biometric_hash(self, fingerprint_template):
        """
        Generate and encrypt a hash from fingerprint template for storage.
        Uses AES-256 encryption for the biometric hash.
        """
        if fingerprint_template:
            from core.utils.encryption import encrypt_biometric_hash
            # First create a SHA-256 hash of the template
            hash_value = hashlib.sha256(fingerprint_template.encode()).hexdigest()
            # Then encrypt it using AES-256
            return encrypt_biometric_hash(hash_value)
        return None
    
    def verify_biometric_hash(self, fingerprint_template):
        """
        Verify a fingerprint template against the stored encrypted hash.
        """
        if not self.biometric_hash or not fingerprint_template:
            return False
        
        from core.utils.encryption import decrypt_biometric_hash
        try:
            # Decrypt the stored hash
            stored_hash = decrypt_biometric_hash(self.biometric_hash)
            # Hash the provided template
            provided_hash = hashlib.sha256(fingerprint_template.encode()).hexdigest()
            # Compare
            return stored_hash == provided_hash
        except Exception:
            return False


# ============================================================================
# 2. STUDENTS TABLE
# ============================================================================

class Student(models.Model):
    """
    Student profile table with academic records.
    One-to-One relationship with Users table.
    Updated to use Department FK per 21-table schema.
    Maintains compatibility with frontend expectations.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    student_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        db_column='user_id'
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Student's department/faculty"
    )
    student_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique student ID number"
    )
    # Frontend compatibility fields
    first_name = models.CharField(
        max_length=100,
        help_text="First name (from user profile)"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Last name (from user profile)"
    )
    grade_level = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Grade level (for frontend compatibility)"
    )
    section = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Section (for frontend compatibility)"
    )
    # 21-table schema fields
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Student's date of birth"
    )
    address = models.TextField(
        null=True,
        blank=True,
        help_text="Student's address"
    )
    enrollment_date = models.DateField(
        default=timezone.now,
        help_text="Date of enrollment"
    )
    academic_year = models.CharField(
        max_length=20,
        default="",
        help_text="Academic year e.g. 2024/2025"
    )
    programme = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Programme of study"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Student status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-populate first_name and last_name from user if not set
        if self.user:
            if not self.first_name:
                self.first_name = self.user.first_name
            if not self.last_name:
                self.last_name = self.user.last_name
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['student_number']),
            models.Index(fields=['status']),
            models.Index(fields=['grade_level']),
        ]
    
    def __str__(self):
        return f"{self.student_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ============================================================================
# 3. STAFF TABLE
# ============================================================================

class Staff(models.Model):
    """
    Staff/Employee profile table.
    One-to-One relationship with Users table.
    Includes shift timing for attendance tracking.
    Updated to use Department FK per 21-table schema.
    """
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
    ]
    
    staff_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        db_column='user_id'
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.PROTECT,
        related_name='staff_members',
        help_text="Department FK"
    )
    staff_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique staff ID number"
    )
    position = models.CharField(
        max_length=150,
        help_text="Staff position/title"
    )
    hire_date = models.DateField(
        help_text="Date of hire"
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of termination (if applicable)"
    )
    # Encrypted salary field (AES-256)
    salary = models.TextField(
        null=True,
        blank=True,
        help_text="Encrypted salary (AES-256)"
    )
    # Shift timing for late detection
    shift_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Shift start time (HH:MM)"
    )
    shift_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Shift end time (HH:MM)"
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        help_text="Employment type"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        indexes = [
            models.Index(fields=['staff_number']),
            models.Index(fields=['department']),
            models.Index(fields=['position']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.staff_number} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()


# ============================================================================
# 4. ATTENDANCE TABLE (Biometric Staff Attendance)
# ============================================================================

class Attendance(models.Model):
    """
    Staff attendance tracking with biometric verification.
    Records clock-in/out with late detection.
    """
    STATUS_CHOICES = [
        ('in', 'Clock In'),
        ('out', 'Clock Out'),
    ]
    
    METHOD_CHOICES = [
        ('biometric', 'Biometric/Fingerprint'),
        ('manual', 'Manual Entry'),
        ('card', 'Card/RFID'),
    ]
    
    att_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        db_column='user_id'
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        db_column='staff_id',
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        help_text="Clock in or out"
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default='biometric'
    )
    is_late = models.BooleanField(
        default=False,
        help_text="True if clock-in is past shift start + threshold"
    )
    late_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of minutes late"
    )
    notes = models.TextField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_attendance',
        help_text="Admin who verified manual entry"
    )
    biometric_match_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Fingerprint match confidence score (0-100)"
    )
    device_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Biometric device identifier"
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="GPS coordinates or location name"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance'
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_late']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.status} at {self.timestamp}"
    
    def check_if_late(self):
        """
        Check if clock-in is late based on staff's shift settings.
        """
        if self.status == 'in' and self.staff:
            from datetime import datetime, timedelta
            
            # Get today's shift start time
            shift_start = datetime.combine(
                self.timestamp.date(),
                self.staff.shift_start_time
            )
            threshold = timedelta(minutes=self.staff.late_threshold_minutes)
            late_threshold = shift_start + threshold
            
            # Check if clock-in is past the threshold
            if self.timestamp > late_threshold:
                self.is_late = True
                self.late_minutes = int((self.timestamp - shift_start).total_seconds() / 60)
            else:
                self.is_late = False
                self.late_minutes = 0
            
            return self.is_late
        return False
    
    def save(self, *args, **kwargs):
        # Auto-check for lateness before saving
        if self.status == 'in':
            self.check_if_late()
        super().save(*args, **kwargs)


# ============================================================================
# STUDENT ATTENDANCE (Separate from Staff Attendance)
# ============================================================================

class StudentAttendance(models.Model):
    """
    Student attendance tracking per course.
    Separate from Staff Attendance.
    Updated to use Semester FK per 21-table schema.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    record_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="Student FK"
    )
    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.CASCADE,
        related_name='student_attendance',
        help_text="Course FK"
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.PROTECT,
        related_name='student_attendance',
        db_column='semester_id',
        null=True,
        blank=True,
        help_text="Semester FK"
    )
    date = models.DateField(
        help_text="Attendance date"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        help_text="Attendance status"
    )
    marked_by = models.ForeignKey(
        'core.Staff',
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendance',
        help_text="Staff who marked attendance"
    )
    notified_parent = models.BooleanField(
        default=False,
        help_text="Flipped after SMS sent"
    )
    
    class Meta:
        db_table = 'student_attendance'
        verbose_name = 'Student Attendance'
        verbose_name_plural = 'Student Attendance Records'
        ordering = ['-date']
        unique_together = ['student', 'course', 'date']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['course']),
            models.Index(fields=['semester']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"


# ============================================================================
# PARENTS TABLE
# ============================================================================

class Parent(models.Model):
    """
    Parent/Guardian table for student notifications.
    """
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]
    
    parent_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        null=True,
        blank=True,
        help_text="Optional portal access"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        help_text="Primary contact for SMS notifications"
    )
    email = models.EmailField(null=True, blank=True)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.BooleanField(default=True)
    # Notification preferences stored as JSON
    notification_prefs = models.JSONField(
        default=dict,
        blank=True,
        help_text="{absence_alerts: bool, grade_updates: bool, general_announcements: bool}"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parents'
        verbose_name = 'Parent/Guardian'
        verbose_name_plural = 'Parents/Guardians'
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['emergency_contact']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.relationship})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ============================================================================
# PARENT-STUDENT LINK TABLE
# ============================================================================

class ParentStudentLink(models.Model):
    """
    Many-to-Many link table between Parents and Students.
    Allows multiple parents per student and vice versa.
    """
    link_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name='student_links'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='parent_links'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary contact for emergency"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'parent_student_links'
        unique_together = ['parent', 'student']
        verbose_name = 'Parent-Student Link'
        verbose_name_plural = 'Parent-Student Links'
    
    def __str__(self):
        return f"{self.parent.full_name} - {self.student.full_name}"


# ============================================================================
# 2. REFRESH TOKENS TABLE
# ============================================================================

class RefreshToken(models.Model):
    """
    JWT refresh token management for secure session handling.
    Supports token revocation and device tracking.
    """
    token_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='refresh_tokens',
        help_text="User who owns this token"
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed refresh token for security"
    )
    device_info = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Browser/device identifier"
    )
    ip_address = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        help_text="IPv4 or IPv6 address"
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When token was issued"
    )
    expires_at = models.DateTimeField(
        help_text="When token expires"
    )
    revoked = models.BooleanField(
        default=False,
        help_text="Set true on logout"
    )
    
    class Meta:
        db_table = 'refresh_tokens'
        verbose_name = 'Refresh Token'
        verbose_name_plural = 'Refresh Tokens'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Token for {self.user.username} - {'Revoked' if self.revoked else 'Active'}"


# ============================================================================
# 3. AUDIT LOG TABLE
# ============================================================================

class AuditLog(models.Model):
    """
    Immutable record of sensitive actions for compliance.
    Append-only table - no updates or deletes permitted.
    """
    log_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=100,
        help_text="e.g. GRADE_UPDATED, LEAVE_APPROVED"
    )
    target_table = models.CharField(
        max_length=100,
        help_text="Which table was affected"
    )
    target_id = models.UUIDField(
        help_text="Which record was affected"
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="State before change"
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        help_text="State after change"
    )
    ip_address = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        help_text="IP address of the actor"
    )
    performed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed"
    )
    
    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['actor']),
            models.Index(fields=['target_table', 'target_id']),
            models.Index(fields=['performed_at']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.target_table} by {self.actor.username} at {self.performed_at}"
