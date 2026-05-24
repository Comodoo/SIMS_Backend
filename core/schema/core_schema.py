"""
Core GraphQL Schema (Strawberry)
Users, Students, Staff, Attendance, Parents, RefreshTokens, AuditLog
Part of 21-Table Schema Implementation
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from core.models.core_models import User, Student, Staff, Attendance, StudentAttendance, Parent


@strawberry.type
class UserType:
    """GraphQL type for User"""
    id: strawberry.ID
    username: str
    email: str
    first_name: str = strawberry.field(name="first_name")
    last_name: str = strawberry.field(name="last_name")
    role: str
    phone: Optional[str] = None
    is_active: bool = strawberry.field(name="is_active")
    created_at: datetime = strawberry.field(name="created_at")
    updated_at: datetime = strawberry.field(name="updated_at")
    
    @classmethod
    def from_model(cls, instance: User):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.user_id)),
            username=instance.username,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            role=instance.role,
            phone=instance.phone,
            is_active=instance.is_active,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class StudentType:
    """GraphQL type for Student (updated for 21-table schema with frontend compatibility)"""
    id: strawberry.ID
    user: UserType
    department_id: Optional[strawberry.ID] = strawberry.field(name="department_id")
    student_number: str = strawberry.field(name="student_number")
    first_name: str = strawberry.field(name="first_name")
    last_name: str = strawberry.field(name="last_name")
    date_of_birth: Optional[date] = strawberry.field(name="date_of_birth")
    address: Optional[str] = None
    enrollment_date: date = strawberry.field(name="enrollment_date")
    status: str
    grade_level: Optional[str] = strawberry.field(name="grade_level")
    section: Optional[str] = None
    academic_year: str = strawberry.field(name="academic_year")
    programme: Optional[str] = None
    created_at: datetime = strawberry.field(name="created_at")
    updated_at: datetime = strawberry.field(name="updated_at")
    
    @classmethod
    def from_model(cls, instance: Student):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.student_id)),
            user=UserType.from_model(instance.user),
            department_id=strawberry.ID(str(instance.department.dept_id)) if instance.department else None,
            student_number=instance.student_number,
            first_name=instance.first_name,
            last_name=instance.last_name,
            date_of_birth=instance.date_of_birth,
            address=instance.address,
            enrollment_date=instance.enrollment_date,
            status=instance.status,
            grade_level=instance.grade_level,
            section=instance.section,
            academic_year=instance.academic_year,
            programme=instance.programme,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class StaffType:
    """GraphQL type for Staff (updated for 21-table schema)"""
    id: strawberry.ID
    user: UserType
    department_id: strawberry.ID = strawberry.field(name="department_id")
    staff_number: str = strawberry.field(name="staff_number")
    position: str
    department: str = strawberry.field(resolver=lambda self: self.department_name)
    hire_date: date = strawberry.field(name="hire_date")
    shift_start_time: Optional[time] = strawberry.field(name="shift_start_time")
    shift_end_time: Optional[time] = strawberry.field(name="shift_end_time")
    late_threshold_minutes: int = strawberry.field(name="late_threshold_minutes")
    is_active: bool = strawberry.field(name="is_active")
    created_at: datetime = strawberry.field(name="created_at")
    updated_at: datetime = strawberry.field(name="updated_at")
    
    # Internal field for resolver
    department_name: strawberry.Private[str]

    @classmethod
    def from_model(cls, instance: Staff):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.staff_id)),
            user=UserType.from_model(instance.user),
            department_id=strawberry.ID(str(instance.department.dept_id)),
            staff_number=instance.staff_number,
            position=instance.position,
            department_name=instance.department.name if instance.department else "N/A",
            hire_date=instance.hire_date,
            shift_start_time=instance.shift_start_time,
            shift_end_time=instance.shift_end_time,
            late_threshold_minutes=15, # Default threshold
            is_active=instance.is_active,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class AttendanceType:
    """GraphQL type for Attendance"""
    id: strawberry.ID
    user: UserType
    staff: Optional[StaffType] = None
    timestamp: datetime
    status: str
    method: str
    is_late: bool = strawberry.field(name="is_late")
    late_minutes: Optional[int] = strawberry.field(name="late_minutes")
    notes: Optional[str] = None
    device_id: Optional[str] = strawberry.field(name="device_id")
    location: Optional[str] = None
    created_at: datetime = strawberry.field(name="created_at")
    
    @classmethod
    def from_model(cls, instance: Attendance):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.att_id)),
            user=UserType.from_model(instance.user),
            staff=StaffType.from_model(instance.staff) if instance.staff else None,
            timestamp=instance.timestamp,
            status=instance.status,
            method=instance.method,
            is_late=instance.is_late,
            late_minutes=instance.late_minutes,
            notes=instance.notes,
            device_id=instance.device_id,
            location=instance.location,
            created_at=instance.created_at,
        )


@strawberry.type
class StudentAttendanceType:
    """GraphQL type for StudentAttendance (updated for 21-table schema with frontend compatibility)"""
    id: strawberry.ID
    studentId: strawberry.ID
    courseId: strawberry.ID
    date: date
    status: str
    remarks: Optional[str] = None
    recordedBy: strawberry.ID
    recordedAt: datetime
    
    @classmethod
    def from_model(cls, instance: StudentAttendance):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.record_id)),
            studentId=strawberry.ID(str(instance.student.student_id)),
            courseId=strawberry.ID(str(instance.course.course_id)),
            date=instance.date,
            status=instance.status,
            remarks=instance.remarks,
            recordedBy=strawberry.ID(str(instance.marked_by.user_id)) if instance.marked_by else None,
            recordedAt=instance.marked_at,
        )


@strawberry.type
class ParentType:
    """GraphQL type for Parent"""
    id: strawberry.ID
    user: Optional[UserType] = None
    firstName: str
    lastName: str
    phone: str
    email: Optional[str] = None
    relationship: str
    address: Optional[str] = None
    emergencyContact: bool
    createdAt: datetime
    updatedAt: datetime
    
    @classmethod
    def from_model(cls, instance: Parent):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.parent_id)),
            user=UserType.from_model(instance.user) if instance.user else None,
            firstName=instance.first_name,
            lastName=instance.last_name,
            phone=instance.phone,
            email=instance.email,
            relationship=instance.relationship,
            address=instance.address,
            emergencyContact=instance.emergency_contact,
            createdAt=instance.created_at,
            updatedAt=instance.updated_at,
        )


# Input Types for Mutations
@strawberry.input
class UserInput:
    """Input for creating/updating User"""
    username: str
    email: str
    firstName: str
    lastName: str
    password: Optional[str] = None
    role: str
    phone: Optional[str] = None


@strawberry.input
class StudentInput:
    """Input for creating/updating Student"""
    user: UserInput
    student_number: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    grade_level: Optional[str] = None
    section: Optional[str] = None


@strawberry.input
class StaffInput:
    """Input for creating/updating Staff"""
    user: UserInput
    staff_number: str
    position: str
    department: str
    hire_date: date
    shift_start_time: time
    shift_end_time: time
    late_threshold_minutes: int = 15


@strawberry.input
class AttendanceInput:
    """Input for creating Attendance record"""
    user_id: strawberry.ID
    status: str
    method: str = "biometric"
    device_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


# Response Types for Mutations
@strawberry.type
class UserMutationResponse:
    """Response for User mutations"""
    success: bool
    message: str
    user: Optional[UserType] = None


@strawberry.type
class AttendanceMutationResponse:
    """Response for Attendance mutations"""
    success: bool
    message: str
    attendance: Optional[AttendanceType] = None
