"""
Core GraphQL Queries (Strawberry)
"""

import strawberry
from typing import Optional, List
from django.contrib.auth import get_user_model
from core.models.core_models import User, Student, Staff, Attendance, StudentAttendance, Parent
from core.schema.core_schema import UserType, StudentType, StaffType, AttendanceType, StudentAttendanceType, ParentType
from academics.schema.academics_schema import EnrollmentType, AssignmentType


@strawberry.type
class CoreQuery:
    """GraphQL queries for Core module"""
    
    @strawberry.field
    def users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[UserType]:
        """Query users with filters"""
        queryset = User.objects.all()
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return [UserType.from_model(user) for user in queryset[offset:offset+limit]]
    
    @strawberry.field
    def user(self, id: strawberry.ID) -> Optional[UserType]:
        """Get user by ID"""
        try:
            instance = User.objects.get(user_id=id)
            return UserType.from_model(instance)
        except User.DoesNotExist:
            return None
    
    @strawberry.field
    def students(
        self,
        status: Optional[str] = None,
        grade_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[StudentType]:
        """Query students with filters"""
        queryset = Student.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        return [StudentType.from_model(student) for student in queryset[offset:offset+limit]]
    
    @strawberry.field
    def enrollments(
        self,
        student_id: Optional[strawberry.ID] = None,
        course_id: Optional[strawberry.ID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[EnrollmentType]:
        """Query enrollments with filters (for frontend compatibility)"""
        from academics.models.academics_models import Enrollment
        queryset = Enrollment.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if status:
            queryset = queryset.filter(status=status)
        return [EnrollmentType.from_model(enrollment) for enrollment in queryset[offset:offset+limit]]
    
    @strawberry.field
    def student(self, id: strawberry.ID) -> Optional[StudentType]:
        """Get student by ID"""
        try:
            instance = Student.objects.get(student_id=id)
            return StudentType.from_model(instance)
        except Student.DoesNotExist:
            return None
    
    @strawberry.field
    def student_by_number(self, student_number: str) -> Optional[StudentType]:
        """Get student by student number"""
        try:
            instance = Student.objects.get(student_number=student_number)
            return StudentType.from_model(instance)
        except Student.DoesNotExist:
            return None
    
    @strawberry.field(name="staff")
    def staff_members(
        self,
        department: Optional[str] = None,
        position: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[StaffType]:
        """Query staff members with filters"""
        queryset = Staff.objects.all()
        if department:
            queryset = queryset.filter(department=department)
        if position:
            queryset = queryset.filter(position=position)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return [StaffType.from_model(staff) for staff in queryset[offset:offset+limit]]
    
    @strawberry.field
    def staff(self, id: strawberry.ID) -> Optional[StaffType]:
        """Get staff member by ID"""
        try:
            instance = Staff.objects.get(staff_id=id)
            return StaffType.from_model(instance)
        except Staff.DoesNotExist:
            return None
    
    @strawberry.field
    def staff_by_number(self, staff_number: str) -> Optional[StaffType]:
        """Get staff by staff number"""
        try:
            instance = Staff.objects.get(staff_number=staff_number)
            return StaffType.from_model(instance)
        except Staff.DoesNotExist:
            return None
    
    @strawberry.field(name="attendance")
    def attendance_records(
        self,
        user_id: Optional[strawberry.ID] = None,
        status: Optional[str] = None,
        is_late: Optional[bool] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AttendanceType]:
        """Query attendance records with filters"""
        queryset = Attendance.objects.all()
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)
        if is_late is not None:
            queryset = queryset.filter(is_late=is_late)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        return [AttendanceType.from_model(record) for record in queryset[offset:offset+limit]]
    
    @strawberry.field
    def student_attendance_records(
        self,
        student_id: Optional[strawberry.ID] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[StudentAttendanceType]:
        """Query student attendance records with filters (for frontend compatibility)"""
        queryset = StudentAttendance.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return [StudentAttendanceType.from_model(record) for record in queryset[offset:offset+limit]]
    
    @strawberry.field
    def assignments(
        self,
        course_id: Optional[strawberry.ID] = None,
        is_published: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssignmentType]:
        """Query assignments with filters (for frontend compatibility)"""
        from academics.models.academics_models import Assignment
        queryset = Assignment.objects.all()
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published)
        return [AssignmentType.from_model(assignment) for assignment in queryset[offset:offset+limit]]
    
    @strawberry.field
    def parents(
        self,
        relationship: Optional[str] = None,
        emergency_contact: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ParentType]:
        """Query parents with filters"""
        queryset = Parent.objects.all()
        if relationship:
            queryset = queryset.filter(relationship=relationship)
        if emergency_contact is not None:
            queryset = queryset.filter(emergency_contact=emergency_contact)
        return [ParentType.from_model(parent) for parent in queryset[offset:offset+limit]]
    
    @strawberry.field
    def parent(self, id: strawberry.ID) -> Optional[ParentType]:
        """Get parent by ID"""
        try:
            instance = Parent.objects.get(parent_id=id)
            return ParentType.from_model(instance)
        except Parent.DoesNotExist:
            return None
