"""
Academics Admin Configuration
"""
from django.contrib import admin
from .models import Course, Enrollment, Assignment, Submission


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Course admin configuration."""
    list_display = ['course_code', 'name', 'staff', 'credits', 'status']
    list_filter = ['status', 'semester']
    search_fields = ['course_code', 'name', 'description']
    readonly_fields = ['course_id', 'created_at', 'updated_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Enrollment admin configuration."""
    list_display = ['student', 'course', 'semester', 'status', 'final_grade']
    list_filter = ['status', 'semester']
    search_fields = ['student__first_name', 'course__name']
    readonly_fields = ['enrollment_id', 'enrolled_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Assignment admin configuration."""
    list_display = ['title', 'course', 'due_date', 'total_marks', 'is_overdue']
    list_filter = ['course', 'attachment_type']
    search_fields = ['title', 'description']
    readonly_fields = ['assign_id', 'created_at', 'updated_at']
    
    @admin.display(boolean=True, description='Overdue')
    def is_overdue(self, obj):
        return obj.is_overdue


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Submission admin configuration."""
    list_display = ['student', 'assignment', 'submitted_at', 'status', 'grade']
    list_filter = ['status', 'submitted_at']
    search_fields = ['student__first_name', 'assignment__title']
    readonly_fields = ['sub_id', 'created_at', 'updated_at']
