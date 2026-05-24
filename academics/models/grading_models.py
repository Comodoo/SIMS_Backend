"""
Grading Models - GradeComponents, StudentGradeComponents
Part of 21-Table Schema Implementation
"""
import uuid
from django.db import models


# ============================================================================
# 10. GRADE COMPONENTS TABLE
# ============================================================================

class GradeComponent(models.Model):
    """
    Defines the grading structure per course.
    Supports CAT 1, CAT 2, final exam, assignments with weight percentages.
    """
    TYPE_CHOICES = [
        ('cat', 'Continuous Assessment Test'),
        ('exam', 'Examination'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
    ]
    
    component_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.CASCADE,
        related_name='grade_components',
        help_text="Course this component belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="e.g. CAT 1, Final Exam"
    )
    weight_percent = models.FloatField(
        help_text="Weight percentage (must sum to 100 per course)"
    )
    max_score = models.FloatField(
        default=100.0,
        help_text="Maximum possible score"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Due date for this component"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="Type of grade component"
    )
    
    class Meta:
        db_table = 'grade_components'
        verbose_name = 'Grade Component'
        verbose_name_plural = 'Grade Components'
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"{self.course.course_code} - {self.name} ({self.weight_percent}%)"


# ============================================================================
# 11. STUDENT GRADE COMPONENTS TABLE
# ============================================================================

class StudentGradeComponent(models.Model):
    """
    Stores each student's actual score for each grade component.
    The final_grade on Enrollment is computed from this table.
    """
    sgc_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    enrollment = models.ForeignKey(
        'academics.Enrollment',
        on_delete=models.CASCADE,
        related_name='grade_components',
        help_text="Student's enrollment in the course"
    )
    component = models.ForeignKey(
        GradeComponent,
        on_delete=models.CASCADE,
        related_name='student_grades',
        help_text="The grade component being scored"
    )
    score = models.FloatField(
        null=True,
        blank=True,
        help_text="Student's score (null until graded)"
    )
    graded_by = models.ForeignKey(
        'core.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_components',
        help_text="Staff member who graded this"
    )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the grade was assigned"
    )
    remarks = models.TextField(
        null=True,
        blank=True,
        help_text="Additional remarks on the grade"
    )
    
    class Meta:
        db_table = 'student_grade_components'
        verbose_name = 'Student Grade Component'
        verbose_name_plural = 'Student Grade Components'
        unique_together = ['enrollment', 'component']
        indexes = [
            models.Index(fields=['enrollment']),
            models.Index(fields=['component']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.component.name}: {self.score or 'Not graded'}"
