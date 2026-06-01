"""
Django Admin Configuration for Core Models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Staff, Attendance, StudentAttendance


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """User admin configuration."""
    list_display = ['username', 'email', 'role', 'is_active', 'last_login', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email']
    readonly_fields = ['user_id', 'created_at', 'updated_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'biometric_hash')
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student admin configuration."""
    list_display = ['student_number', 'full_name', 'status', 'grade_level', 'enrollment_date']
    list_filter = ['status', 'grade_level', 'enrollment_date']
    search_fields = ['student_number', 'first_name', 'last_name']
    readonly_fields = ['student_id', 'created_at', 'updated_at']
    
    @admin.display(description='Full Name')
    def full_name(self, obj):
        return obj.full_name


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Staff admin configuration."""
    list_display = ['staff_number', 'full_name', 'position', 'department', 'is_active']
    list_filter = ['position', 'department', 'is_active', 'hire_date']
    search_fields = ['staff_number', 'user__first_name', 'user__last_name']
    readonly_fields = ['staff_id', 'created_at', 'updated_at']
    
    @admin.display(description='Full Name')
    def full_name(self, obj):
        return obj.full_name


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Attendance admin configuration."""
    list_display = ['user', 'staff', 'timestamp', 'status', 'is_late', 'method']
    list_filter = ['status', 'is_late', 'method', 'timestamp']
    search_fields = ['user__username', 'staff__staff_number']
    readonly_fields = ['att_id', 'created_at']
    date_hierarchy = 'timestamp'


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    """Student attendance admin configuration."""
    list_display = ['student', 'course', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['student__first_name', 'student__last_name']
    readonly_fields = ['record_id']
    date_hierarchy = 'date'


