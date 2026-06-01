"""
Core GraphQL Schema (Strawberry)
Users, Students, Staff, Attendance, RefreshTokens, AuditLog
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from core.models.core_models import User, Student, Staff, Attendance, StudentAttendance, AttendanceSession, SystemSettings


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
            department_id=strawberry.ID(str(instance.department.dept_id)) if instance.department else strawberry.ID(''),
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
    """GraphQL type for StudentAttendance"""
    id: strawberry.ID
    studentId: strawberry.ID
    studentName: str
    courseId: strawberry.ID
    courseName: str
    date: date
    status: str
    method: str
    markedAt: Optional[datetime] = None
    markedById: Optional[strawberry.ID] = None
    markedByName: Optional[str] = None

    @classmethod
    def from_model(cls, instance: StudentAttendance):
        marker = instance.marked_by
        return cls(
            id=strawberry.ID(str(instance.record_id)),
            studentId=strawberry.ID(str(instance.student.student_id)),
            studentName=instance.student.full_name,
            courseId=strawberry.ID(str(instance.course.course_id)),
            courseName=instance.course.name,
            date=instance.date,
            status=instance.status,
            method=instance.method,
            markedAt=instance.marked_at,
            markedById=strawberry.ID(str(marker.staff_id)) if marker else None,
            markedByName=marker.user.get_full_name() if marker else None,
        )


@strawberry.type
class AttendanceSessionType:
    """GraphQL type for AttendanceSession"""
    id: strawberry.ID
    courseId: strawberry.ID
    courseName: str
    semesterId: Optional[strawberry.ID] = None
    date: date
    conductedById: Optional[strawberry.ID] = None
    conductedByName: Optional[str] = None
    wasHeld: bool
    cancellationReason: Optional[str] = None
    createdAt: datetime

    @classmethod
    def from_model(cls, instance: AttendanceSession):
        conductor = instance.conducted_by
        return cls(
            id=strawberry.ID(str(instance.session_id)),
            courseId=strawberry.ID(str(instance.course.course_id)),
            courseName=instance.course.name,
            semesterId=strawberry.ID(str(instance.semester_id)) if instance.semester_id else None,
            date=instance.date,
            conductedById=strawberry.ID(str(conductor.staff_id)) if conductor else None,
            conductedByName=conductor.user.get_full_name() if conductor else None,
            wasHeld=instance.was_held,
            cancellationReason=instance.cancellation_reason,
            createdAt=instance.created_at,
        )


@strawberry.type
class SystemSettingType:
    """GraphQL type for SystemSettings"""
    id: strawberry.ID
    key: str
    value: str
    description: Optional[str] = None
    updatedAt: datetime

    @classmethod
    def from_model(cls, instance: SystemSettings):
        return cls(
            id=strawberry.ID(str(instance.setting_id)),
            key=instance.key,
            value=instance.value,
            description=instance.description,
            updatedAt=instance.updated_at,
        )


@strawberry.type
class StudentAttendanceRateType:
    """Aggregate attendance rate for a student in a course"""
    courseId: strawberry.ID
    courseName: str
    totalSessions: int
    present: int
    late: int
    absent: int
    excused: int
    attendanceRate: float
    belowThreshold: bool


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


@strawberry.input
class RegisterStudentInput:
    """Flat input for admin to register a new student (creates User + Student profile)"""
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    student_number: str
    grade_level: Optional[str] = None
    section: Optional[str] = None
    department_id: Optional[strawberry.ID] = None
    academic_year: str = ""
    phone: Optional[str] = None


@strawberry.input
class SelfRegisterStudentInput:
    """Minimal input for a student to self-register (no admin privileges required)."""
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    class_group_id: Optional[strawberry.ID] = None


@strawberry.input
class UpdateStudentInput:
    """Fields for updating an existing student (all optional)."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    grade_level: Optional[str] = None
    section: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None


@strawberry.input
class RegisterStaffInput:
    """Flat input for admin to register a new staff/teacher (creates User + Staff profile)"""
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    staff_number: str
    position: str
    department_id: strawberry.ID
    phone: Optional[str] = None


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


@strawberry.type
class ClassGroupType:
    id: strawberry.ID
    name: str
    student_count: int = strawberry.field(name="studentCount")
    active_count: int = strawberry.field(name="activeCount")
    created_at: datetime = strawberry.field(name="createdAt")
    parent_id: Optional[strawberry.ID] = strawberry.field(name="parentId", default=None)

    @classmethod
    def from_model(cls, instance, student_count: int = 0, active_count: int = 0):
        return cls(
            id=strawberry.ID(str(instance.id)),
            name=instance.name,
            student_count=student_count,
            active_count=active_count,
            created_at=instance.created_at,
            parent_id=strawberry.ID(str(instance.parent_id)) if instance.parent_id else None,
        )


@strawberry.type
class ClassGroupMutationResponse:
    success: bool
    message: str
    class_group: Optional[ClassGroupType] = strawberry.field(name="classGroup", default=None)
