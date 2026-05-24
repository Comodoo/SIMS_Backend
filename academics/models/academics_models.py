"""
Academics Models - Courses, Enrollment, Assignments, Submissions
Part of 21-Table Schema Implementation
"""
import uuid
from django.db import models
from django.utils import timezone


class Course(models.Model):
    """
    Course catalog table.
    Updated to use Department and Semester FKs per 21-table schema.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    course_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=200,
        help_text="Course name"
    )
    course_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="e.g. CS301"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Course description"
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.PROTECT,
        related_name='courses',
        help_text="Department FK"
    )
    staff = models.ForeignKey(
        'core.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses_teaching',
        db_column='staff_id',
        help_text="Primary lecturer"
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.PROTECT,
        related_name='courses',
        db_column='semester_id',
        help_text="Semester FK"
    )
    credits = models.IntegerField(
        default=3,
        help_text="Credit hours"
    )
    max_students = models.IntegerField(
        default=30,
        help_text="Maximum enrollment"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Course status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        indexes = [
            models.Index(fields=['course_code']),
            models.Index(fields=['status']),
            models.Index(fields=['staff']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.name}"
    
    @property
    def current_enrollment(self):
        """Get current enrollment count."""
        return self.enrollments.filter(status='active').count()
    
    @property
    def available_seats(self):
        """Get available seats."""
        return self.max_students - self.current_enrollment


class Enrollment(models.Model):
    """
    Junction table linking students to courses.
    Updated to use Semester FK per 21-table schema.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    ]
    
    enrollment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    student = models.ForeignKey(
        'core.Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Student FK"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Course FK"
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.PROTECT,
        related_name='enrollments',
        db_column='semester_id',
        help_text="Semester FK"
    )
    enrolled_at = models.DateTimeField(
        default=timezone.now,
        help_text="When student enrolled"
    )
    final_grade = models.FloatField(
        null=True,
        blank=True,
        help_text="Computed from GradeComponents"
    )
    grade_letter = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        help_text="e.g. A, B+"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Enrollment status"
    )
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course', 'semester']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['course']),
            models.Index(fields=['semester']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course.name}"


class Assignment(models.Model):
    """Course assignments and homework."""
    ASSIGNMENT_TYPES = [
        ('homework', 'Homework'),
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('project', 'Project'),
        ('lab', 'Laboratory'),
        ('essay', 'Essay'),
    ]
    
    ATTACHMENT_TYPES = [
        ('pdf', 'PDF Document'),
        ('doc', 'Word Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('link', 'External Link'),
        ('code', 'Code File'),
    ]
    
    assign_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default='homework'
    )
    due_date = models.DateTimeField()
    total_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00
    )
    attachment_url = models.URLField(null=True, blank=True)
    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPES,
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=False)
    allow_late_submission = models.BooleanField(default=False)
    late_penalty_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage deduction per day late"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assignments'
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['due_date']),
            models.Index(fields=['assignment_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.course.name}"
    
    @property
    def is_overdue(self):
        """Check if assignment is past due date."""
        return timezone.now() > self.due_date


class Submission(models.Model):
    """Student assignment submissions."""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late'),
        ('resubmitted', 'Resubmitted'),
    ]
    
    sub_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    student = models.ForeignKey(
        'core.Student',
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    content_text = models.TextField(null=True, blank=True)
    file_url = models.URLField(null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    # Encrypted grade (AES-256)
    grade = models.TextField(
        null=True,
        blank=True,
        help_text="Encrypted grade (AES-256)"
    )
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(
        'core.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    plagiarism_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Plagiarism detection score (0-100)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        unique_together = ['student', 'assignment']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['assignment']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        # Check if submission is late
        if self.submitted_at and self.assignment.due_date:
            if self.submitted_at > self.assignment.due_date:
                self.status = 'late'
        super().save(*args, **kwargs)
