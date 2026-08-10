"""
Grading Models - GradeComponents, StudentGradeComponents, ResultCard
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


# ============================================================================
# RESULT CARD (per-subject, per-semester result for a student)
# ============================================================================

class ResultCard(models.Model):
    """
    Aggregated result for one student in one subject for one semester.
    Computed from StudentGradeComponent scores.
    Admin/teacher runs compute_result_card mutation to populate this.
    """
    GRADE_CHOICES = [
        ('A', 'A — Excellent (80-100)'),
        ('B', 'B — Good (70-79)'),
        ('C', 'C — Average (60-69)'),
        ('D', 'D — Below Average (50-59)'),
        ('E', 'E — Poor (40-49)'),
        ('F', 'F — Fail (0-39)'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft — not visible to student'),
        ('published', 'Published — visible to student'),
    ]

    result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'core.Student',
        on_delete=models.CASCADE,
        related_name='result_cards',
        help_text="Student this result belongs to"
    )
    subject = models.ForeignKey(
        'academics.Course',
        on_delete=models.CASCADE,
        related_name='result_cards',
        help_text="Subject/course"
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.CASCADE,
        related_name='result_cards',
        help_text="Semester/term"
    )
    cat1_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="CAT 1 score"
    )
    cat2_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="CAT 2 score"
    )
    exam_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Final exam score"
    )
    total_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Weighted total (computed)"
    )
    grade_letter = models.CharField(
        max_length=2, choices=GRADE_CHOICES, null=True, blank=True
    )
    remarks = models.TextField(null=True, blank=True)
    computed_by = models.ForeignKey(
        'core.Staff',
        on_delete=models.SET_NULL,
        null=True,
        related_name='computed_results',
        help_text="Teacher who computed/approved this result"
    )
    computed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='published', db_index=True,
        help_text="Draft results are hidden from the student until published"
    )
    batch_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Groups result cards created/updated together in one bulk import, for draft review"
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'result_cards'
        unique_together = ['student', 'subject', 'semester']
        verbose_name = 'Result Card'
        verbose_name_plural = 'Result Cards'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['semester']),
            models.Index(fields=['subject']),
        ]

    def __str__(self):
        return f"{self.student.full_name} | {self.subject.name} | {self.semester.name} — {self.grade_letter or 'Pending'}"

    def compute_grade_letter(self):
        """Derive grade letter from total_score."""
        if self.total_score is None:
            return None
        score = float(self.total_score)
        if score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        elif score >= 40:
            return 'E'
        return 'F'

    DEFAULT_REMARKS = {
        'A': 'Excellent performance.',
        'B': 'Good performance.',
        'C': 'Average performance.',
        'D': 'Below average performance — needs improvement.',
        'E': 'Poor performance — needs significant improvement.',
        'F': 'Failed — requires urgent attention.',
    }

    def default_remark(self):
        """Auto remark derived from the grade letter, used whenever a teacher leaves remarks blank."""
        if not self.grade_letter:
            return None
        return self.DEFAULT_REMARKS.get(self.grade_letter)
