"""
Core GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from core.models.core_models import User, Student, Staff, Attendance, StudentAttendance, Parent, ParentStudentLink
from core.schema.core_schema import UserType, StudentType, StaffType, AttendanceType, StudentAttendanceType, ParentType, UserInput, StudentInput, StaffInput, AttendanceInput


@strawberry.type
class CoreMutationResponse:
    """Response type for core mutations"""
    success: bool
    message: str


@strawberry.type
class LoginResponse(CoreMutationResponse):
    """Response type for login mutation"""
    user: Optional[UserType] = None
    token: Optional[str] = None


@strawberry.type
class UserMutationResponse(CoreMutationResponse):
    """Response type for user mutations"""
    user: Optional[UserType] = None


@strawberry.type
class StudentMutationResponse(CoreMutationResponse):
    """Response type for student mutations"""
    student: Optional[StudentType] = None


@strawberry.type
class StaffMutationResponse(CoreMutationResponse):
    """Response type for staff mutations"""
    staff: Optional[StaffType] = None


@strawberry.type
class AttendanceMutationResponse(CoreMutationResponse):
    """Response type for attendance mutations"""
    attendance: Optional[AttendanceType] = None


def _error_response(message: str) -> CoreMutationResponse:
    """Helper for error responses"""
    return CoreMutationResponse(success=False, message=message)


@strawberry.type
class CoreMutation:
    """GraphQL mutations for Core module"""
    
    @strawberry.mutation
    def login(self, username: str, password: str, role: Optional[str] = None) -> LoginResponse:
        """Login user with username and password"""
        try:
            user = authenticate(username=username, password=password)
            if not user:
                return LoginResponse(success=False, message="Invalid credentials")
            
            # Check role if provided
            if role and user.role != role:
                return LoginResponse(success=False, message=f"User is not a {role}")
            
            if not user.is_active:
                return LoginResponse(success=False, message="Account is inactive")
            
            # Generate token (using user_id as simple token for now - in production use JWT)
            token = str(user.user_id)
            
            return LoginResponse(
                success=True,
                message="Login successful",
                user=UserType.from_model(user),
                token=token
            )
        except Exception as e:
            return LoginResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_user(self, input: UserInput) -> UserMutationResponse:
        """Create a new user"""
        try:
            user = User.objects.create_user(
                username=input.username,
                email=input.email,
                password=input.password,
                first_name=input.firstName,
                last_name=input.lastName,
                role=input.role,
                phone=input.phone
            )
            return UserMutationResponse(
                success=True, 
                message="User created successfully", 
                user=UserType.from_model(user)
            )
        except Exception as e:
            return UserMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def update_user(self, user_id: strawberry.ID, input: UserInput) -> UserMutationResponse:
        """Update an existing user"""
        try:
            user = User.objects.get(user_id=user_id)
            user.username = input.username
            user.email = input.email
            user.first_name = input.first_name
            user.last_name = input.last_name
            user.role = input.role
            user.phone = input.phone
            if input.password:
                user.set_password(input.password)
            user.save()
            return UserMutationResponse(
                success=True, 
                message="User updated successfully", 
                user=UserType.from_model(user)
            )
        except User.DoesNotExist:
            return UserMutationResponse(success=False, message="User not found")
        except Exception as e:
            return UserMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def delete_user(self, user_id: strawberry.ID) -> CoreMutationResponse:
        """Delete a user (soft delete by setting is_active=False)"""
        try:
            user = User.objects.get(user_id=user_id)
            user.is_active = False
            user.save()
            return CoreMutationResponse(success=True, message="User deleted successfully")
        except User.DoesNotExist:
            return CoreMutationResponse(success=False, message="User not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def activate_user(self, user_id: strawberry.ID) -> CoreMutationResponse:
        """Activate a user account"""
        try:
            user = User.objects.get(user_id=user_id)
            user.is_active = True
            user.save()
            return CoreMutationResponse(success=True, message="User activated successfully")
        except User.DoesNotExist:
            return CoreMutationResponse(success=False, message="User not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def deactivate_user(self, user_id: strawberry.ID) -> CoreMutationResponse:
        """Deactivate a user account"""
        try:
            user = User.objects.get(user_id=user_id)
            user.is_active = False
            user.save()
            return CoreMutationResponse(success=True, message="User deactivated successfully")
        except User.DoesNotExist:
            return CoreMutationResponse(success=False, message="User not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_student(self, input: StudentInput) -> StudentMutationResponse:
        """Create a new student"""
        try:
            # Create user first
            user = User.objects.create_user(
                username=input.user.username,
                email=input.user.email,
                password=input.user.password or 'temp123',
                first_name=input.user.first_name,
                last_name=input.user.last_name,
                role='student',
                phone=input.user.phone
            )
            
            # Create student profile
            student = Student.objects.create(
                user=user,
                student_number=input.student_number,
                first_name=input.first_name,
                last_name=input.last_name,
                date_of_birth=input.date_of_birth,
                address=input.address,
                grade_level=input.grade_level,
                section=input.section
            )
            
            return StudentMutationResponse(
                success=True, 
                message="Student created successfully", 
                student=StudentType.from_model(student)
            )
        except Exception as e:
            return StudentMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_staff(self, input: StaffInput) -> StaffMutationResponse:
        """Create a new staff member"""
        try:
            # Create user first
            user = User.objects.create_user(
                username=input.user.username,
                email=input.user.email,
                password=input.user.password or 'temp123',
                first_name=input.user.first_name,
                last_name=input.user.last_name,
                role='staff',
                phone=input.user.phone
            )
            
            # Create staff profile
            staff = Staff.objects.create(
                user=user,
                staff_number=input.staff_number,
                position=input.position,
                department=input.department,
                hire_date=input.hire_date,
                shift_start_time=input.shift_start_time,
                shift_end_time=input.shift_end_time,
                late_threshold_minutes=input.late_threshold_minutes or 15
            )
            
            return StaffMutationResponse(
                success=True, 
                message="Staff created successfully", 
                staff=StaffType.from_model(staff)
            )
        except Exception as e:
            return StaffMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def clock_in(self, input: AttendanceInput) -> AttendanceMutationResponse:
        """Clock in staff member"""
        try:
            user = User.objects.get(user_id=input.user_id)
            staff = Staff.objects.get(user=user)
            
            attendance = Attendance.objects.create(
                user=user,
                staff=staff,
                status='in',
                method=input.method or 'biometric',
                device_id=input.device_id,
                location=input.location,
                notes=input.notes
            )
            
            return AttendanceMutationResponse(
                success=True, 
                message="Clocked in successfully", 
                attendance=AttendanceType.from_model(attendance)
            )
        except User.DoesNotExist:
            return AttendanceMutationResponse(success=False, message="User not found")
        except Staff.DoesNotExist:
            return AttendanceMutationResponse(success=False, message="Staff profile not found")
        except Exception as e:
            return AttendanceMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def clock_out(self, input: AttendanceInput) -> AttendanceMutationResponse:
        """Clock out staff member"""
        try:
            user = User.objects.get(user_id=input.user_id)
            staff = Staff.objects.get(user=user)
            
            attendance = Attendance.objects.create(
                user=user,
                staff=staff,
                status='out',
                method=input.method or 'biometric',
                device_id=input.device_id,
                location=input.location,
                notes=input.notes
            )
            
            return AttendanceMutationResponse(
                success=True, 
                message="Clocked out successfully", 
                attendance=AttendanceType.from_model(attendance)
            )
        except User.DoesNotExist:
            return AttendanceMutationResponse(success=False, message="User not found")
        except Staff.DoesNotExist:
            return AttendanceMutationResponse(success=False, message="Staff profile not found")
        except Exception as e:
            return AttendanceMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def mark_student_attendance(self, student_id: strawberry.ID, status: str, course_id: Optional[strawberry.ID] = None, marked_by_id: Optional[strawberry.ID] = None, notes: Optional[str] = None) -> CoreMutationResponse:
        """Mark student attendance (biometric/manual)"""
        try:
            student = Student.objects.get(student_id=student_id)
            
            attendance = StudentAttendance.objects.create(
                student=student,
                course_id=course_id,
                status=status,
                marked_by_id=marked_by_id,
                notes=notes
            )
            
            return CoreMutationResponse(success=True, message="Student attendance marked successfully")
        except Student.DoesNotExist:
            return CoreMutationResponse(success=False, message="Student not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def mark_student_biometric_attendance(self, student_id: strawberry.ID, course_id: strawberry.ID, biometric_hash: str) -> CoreMutationResponse:
        """Mark student attendance using biometric verification"""
        try:
            student = Student.objects.get(student_id=student_id)
            user = student.user
            
            # Verify biometric hash (simplified - in production use proper biometric matching)
            if user.biometric_hash != biometric_hash:
                return CoreMutationResponse(success=False, message="Biometric verification failed")
            
            attendance = StudentAttendance.objects.create(
                student=student,
                course_id=course_id,
                status='present',
                marked_by=user,
                notes='Biometric verified'
            )
            
            return CoreMutationResponse(success=True, message="Biometric attendance marked successfully")
        except Student.DoesNotExist:
            return CoreMutationResponse(success=False, message="Student not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")
