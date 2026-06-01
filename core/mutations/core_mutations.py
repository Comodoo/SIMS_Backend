"""
Core GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional, List
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone


@strawberry.input
class StudentAttendanceInput:
    student_id: strawberry.ID
    status: str  # present | absent | late | excused
from core.models.core_models import User, Student, Staff, Attendance, StudentAttendance, AttendanceSession, SystemSettings
from core.schema.core_schema import (
    UserType, StudentType, StaffType, AttendanceType, StudentAttendanceType,
    AttendanceSessionType, SystemSettingType,
    UserInput, StudentInput, StaffInput, AttendanceInput, RegisterStudentInput, RegisterStaffInput,
    UpdateStudentInput, ClassGroupType, ClassGroupMutationResponse, SelfRegisterStudentInput,
)


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

    # ------------------------------------------------------------------
    # Attendance Sessions
    # ------------------------------------------------------------------

    @strawberry.mutation
    def create_attendance_session(
        self,
        course_id: strawberry.ID,
        date: str,
        teacher_id: strawberry.ID,
        semester_id: Optional[strawberry.ID] = None,
        was_held: bool = True,
        cancellation_reason: Optional[str] = None,
    ) -> CoreMutationResponse:
        """Create (or get-or-create) an attendance session for a class on a date."""
        from django.db import IntegrityError
        try:
            from academics.models.academics_models import Course
            from academics.models.academic_structure_models import Semester
            course = Course.objects.get(course_id=course_id)
            teacher = Staff.objects.get(staff_id=teacher_id)
            semester = None
            if semester_id:
                try:
                    semester = Semester.objects.get(semester_id=semester_id)
                except Semester.DoesNotExist:
                    pass
            session, created = AttendanceSession.objects.get_or_create(
                course=course,
                date=date,
                defaults=dict(
                    conducted_by=teacher,
                    semester=semester,
                    was_held=was_held,
                    cancellation_reason=cancellation_reason,
                ),
            )
            if not created:
                session.conducted_by = teacher
                session.was_held = was_held
                session.cancellation_reason = cancellation_reason
                if semester:
                    session.semester = semester
                session.save()
            verb = 'created' if created else 'updated'
            return CoreMutationResponse(success=True, message=f"Attendance session {verb} successfully")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Bulk student attendance marking
    # ------------------------------------------------------------------

    @strawberry.mutation
    def mark_student_attendance_bulk(
        self,
        course_id: strawberry.ID,
        date: str,
        teacher_id: strawberry.ID,
        records: List['StudentAttendanceInput'],
        semester_id: Optional[strawberry.ID] = None,
    ) -> CoreMutationResponse:
        """Mark attendance for multiple students in a course on a date."""
        from django.db import transaction
        from academics.models.academics_models import Course
        from academics.models.academic_structure_models import Semester
        try:
            course = Course.objects.get(course_id=course_id)
            teacher = Staff.objects.get(staff_id=teacher_id)
            semester = None
            if semester_id:
                try:
                    semester = Semester.objects.get(semester_id=semester_id)
                except Semester.DoesNotExist:
                    pass
            saved = 0
            with transaction.atomic():
                for rec in records:
                    student = Student.objects.get(student_id=rec.student_id)
                    obj, _ = StudentAttendance.objects.update_or_create(
                        student=student,
                        course=course,
                        date=date,
                        defaults=dict(
                            status=rec.status,
                            marked_by=teacher,
                            semester=semester,
                            method='manual',
                        ),
                    )
                    saved += 1
            return CoreMutationResponse(success=True, message=f"{saved} attendance records saved")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Manual clock correction (admin)
    # ------------------------------------------------------------------

    @strawberry.mutation
    def manual_clock_correction(
        self,
        staff_id: strawberry.ID,
        clock_in_time: Optional[str] = None,
        clock_out_time: Optional[str] = None,
        date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> CoreMutationResponse:
        """Admin manually corrects a staff member's attendance record."""
        from datetime import datetime as dt
        from django.utils import timezone as tz
        try:
            staff = Staff.objects.get(staff_id=staff_id)
            target_date = date or tz.localdate().isoformat()
            if clock_in_time:
                ts = dt.fromisoformat(f"{target_date}T{clock_in_time}")
                att, _ = Attendance.objects.update_or_create(
                    staff=staff,
                    user=staff.user,
                    timestamp__date=target_date,
                    status='in',
                    defaults=dict(timestamp=ts, method='manual', notes=notes),
                )
                att.check_if_late()
                att.save()
            if clock_out_time:
                ts = dt.fromisoformat(f"{target_date}T{clock_out_time}")
                Attendance.objects.update_or_create(
                    staff=staff,
                    user=staff.user,
                    timestamp__date=target_date,
                    status='out',
                    defaults=dict(timestamp=ts, method='manual', notes=notes),
                )
            return CoreMutationResponse(success=True, message="Attendance corrected successfully")
        except Staff.DoesNotExist:
            return CoreMutationResponse(success=False, message="Staff not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # System settings
    # ------------------------------------------------------------------

    @strawberry.mutation
    def update_system_setting(
        self,
        key: str,
        value: str,
        updated_by_id: Optional[strawberry.ID] = None,
        description: Optional[str] = None,
    ) -> CoreMutationResponse:
        """Create or update a system setting key."""
        try:
            updated_by = None
            if updated_by_id:
                try:
                    updated_by = User.objects.get(user_id=updated_by_id)
                except User.DoesNotExist:
                    pass
            defaults = dict(value=value, updated_by=updated_by)
            if description is not None:
                defaults['description'] = description
            SystemSettings.objects.update_or_create(key=key, defaults=defaults)
            return CoreMutationResponse(success=True, message=f"Setting '{key}' updated to '{value}'")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Staff shift schedule
    # ------------------------------------------------------------------

    @strawberry.mutation
    def update_staff_shift(
        self,
        staff_id: strawberry.ID,
        shift_start_time: Optional[str] = None,   # "HH:MM"
        shift_end_time: Optional[str] = None,      # "HH:MM"
    ) -> CoreMutationResponse:
        """Set the expected clock-in / clock-out times for a staff member."""
        from datetime import time as dt_time
        try:
            staff = Staff.objects.get(staff_id=staff_id)

            if shift_start_time is not None:
                if shift_start_time == '':
                    staff.shift_start_time = None
                else:
                    parts = shift_start_time.split(':')
                    staff.shift_start_time = dt_time(int(parts[0]), int(parts[1]))

            if shift_end_time is not None:
                if shift_end_time == '':
                    staff.shift_end_time = None
                else:
                    parts = shift_end_time.split(':')
                    staff.shift_end_time = dt_time(int(parts[0]), int(parts[1]))

            staff.save(update_fields=['shift_start_time', 'shift_end_time'])
            name = staff.user.get_full_name() or staff.staff_number
            return CoreMutationResponse(success=True, message=f"Shift updated for {name}")
        except Staff.DoesNotExist:
            return CoreMutationResponse(success=False, message="Staff not found")
        except Exception as e:
            return CoreMutationResponse(success=False, message=f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Admin Registration — create User + profile in a single call
    # ------------------------------------------------------------------

    @strawberry.mutation
    def update_student(
        self,
        student_id: strawberry.ID,
        input: UpdateStudentInput,
    ) -> StudentMutationResponse:
        """Update a student's profile and user account fields."""
        try:
            student = Student.objects.select_related('user').get(student_id=student_id)
            user    = student.user
            if input.first_name  is not None: student.first_name  = user.first_name  = input.first_name
            if input.last_name   is not None: student.last_name   = user.last_name   = input.last_name
            if input.email       is not None: user.email          = input.email
            if input.phone       is not None: user.phone          = input.phone
            if input.grade_level is not None: student.grade_level = input.grade_level
            if input.section     is not None: student.section     = input.section
            if input.status      is not None: student.status      = input.status
            if input.address     is not None: student.address     = input.address
            student.save()
            user.save()
            return StudentMutationResponse(
                success=True, message="Student updated successfully",
                student=StudentType.from_model(student),
            )
        except Student.DoesNotExist:
            return StudentMutationResponse(success=False, message="Student not found")
        except Exception as e:
            return StudentMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def register_student(self, input: RegisterStudentInput) -> StudentMutationResponse:
        """Admin registers a new student — creates User account + Student profile."""
        from django.db import transaction
        try:
            with transaction.atomic():
                if User.objects.filter(username=input.username).exists():
                    return StudentMutationResponse(success=False, message=f"Username '{input.username}' is already taken")

                user = User.objects.create_user(
                    username=input.username,
                    email=input.email,
                    password=input.password,
                    first_name=input.first_name,
                    last_name=input.last_name,
                    role='student',
                    phone=input.phone,
                )

                dept = None
                if input.department_id:
                    from academics.models.academic_structure_models import Department
                    try:
                        dept = Department.objects.get(dept_id=input.department_id)
                    except Department.DoesNotExist:
                        pass

                student = Student.objects.create(
                    user=user,
                    department=dept,
                    student_number=input.student_number,
                    first_name=input.first_name,
                    last_name=input.last_name,
                    grade_level=input.grade_level,
                    section=input.section,
                    academic_year=input.academic_year,
                    status='active',
                )
                return StudentMutationResponse(
                    success=True,
                    message="Student registered successfully",
                    student=StudentType.from_model(student),
                )
        except Exception as e:
            return StudentMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def register_staff(self, input: RegisterStaffInput) -> StaffMutationResponse:
        """Admin registers a new staff/teacher — creates User account + Staff profile."""
        from django.db import transaction
        import datetime
        try:
            with transaction.atomic():
                if User.objects.filter(username=input.username).exists():
                    return StaffMutationResponse(success=False, message=f"Username '{input.username}' is already taken")

                from academics.models.academic_structure_models import Department
                try:
                    dept = Department.objects.get(dept_id=input.department_id)
                except Department.DoesNotExist:
                    return StaffMutationResponse(success=False, message="Department not found")

                user = User.objects.create_user(
                    username=input.username,
                    email=input.email,
                    password=input.password,
                    first_name=input.first_name,
                    last_name=input.last_name,
                    role='staff',
                    phone=input.phone,
                )

                staff = Staff.objects.create(
                    user=user,
                    department=dept,
                    staff_number=input.staff_number,
                    position=input.position,
                    hire_date=datetime.date.today(),
                    is_active=True,
                )
                return StaffMutationResponse(
                    success=True,
                    message="Staff registered successfully",
                    staff=StaffType.from_model(staff),
                )
        except Exception as e:
            return StaffMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def self_register_student(self, input: SelfRegisterStudentInput) -> StudentMutationResponse:
        """Public self-registration for students — no auth required."""
        from django.db import transaction
        import uuid
        try:
            with transaction.atomic():
                username = input.username.strip()
                if not username:
                    return StudentMutationResponse(success=False, message="Username cannot be empty")
                if User.objects.filter(username__iexact=username).exists():
                    return StudentMutationResponse(success=False, message=f"Username '{username}' is already taken")
                if User.objects.filter(email__iexact=input.email.strip()).exists():
                    return StudentMutationResponse(success=False, message="An account with that email already exists")

                user = User.objects.create_user(
                    username=username,
                    email=input.email.strip(),
                    password=input.password,
                    first_name=input.first_name.strip(),
                    last_name=input.last_name.strip(),
                    role='student',
                    phone=input.phone,
                )

                class_group = None
                if input.class_group_id:
                    try:
                        from core.models.core_models import ClassGroup
                        class_group = ClassGroup.objects.get(id=input.class_group_id)
                    except ClassGroup.DoesNotExist:
                        pass

                student_number = f"STD-{str(uuid.uuid4())[:8].upper()}"
                while Student.objects.filter(student_number=student_number).exists():
                    student_number = f"STD-{str(uuid.uuid4())[:8].upper()}"

                student = Student.objects.create(
                    user=user,
                    student_number=student_number,
                    first_name=input.first_name.strip(),
                    last_name=input.last_name.strip(),
                    grade_level=class_group.name if class_group else None,
                    status='active',
                )
                return StudentMutationResponse(
                    success=True,
                    message="Account created successfully. You can now log in.",
                    student=StudentType.from_model(student),
                )
        except Exception as e:
            return StudentMutationResponse(success=False, message=f"Error: {str(e)}")

    # ── Class Groups ──────────────────────────────────────────────────────────

    @strawberry.mutation
    def create_class_group(self, name: str, parent_id: Optional[strawberry.ID] = None) -> ClassGroupMutationResponse:
        from core.models.core_models import ClassGroup
        name = name.strip()
        if not name:
            return ClassGroupMutationResponse(success=False, message="Name cannot be empty")
        if ClassGroup.objects.filter(name__iexact=name).exists():
            return ClassGroupMutationResponse(success=False, message=f'"{name}" already exists')
        parent = None
        if parent_id:
            try:
                parent = ClassGroup.objects.get(id=parent_id)
                if parent.parent_id:
                    return ClassGroupMutationResponse(success=False, message="Cannot nest more than one level deep")
            except ClassGroup.DoesNotExist:
                return ClassGroupMutationResponse(success=False, message="Parent group not found")
        cg = ClassGroup.objects.create(name=name, parent=parent)
        count = Student.objects.filter(grade_level=cg.name).count()
        active = Student.objects.filter(grade_level=cg.name, status='active').count()
        return ClassGroupMutationResponse(
            success=True, message="Class group created",
            class_group=ClassGroupType.from_model(cg, student_count=count, active_count=active),
        )

    @strawberry.mutation
    def delete_class_group(self, id: strawberry.ID) -> ClassGroupMutationResponse:
        from core.models.core_models import ClassGroup
        try:
            cg = ClassGroup.objects.get(id=id)
            cg.delete()
            return ClassGroupMutationResponse(success=True, message="Class group deleted")
        except ClassGroup.DoesNotExist:
            return ClassGroupMutationResponse(success=False, message="Class group not found")

    @strawberry.mutation
    def rename_class_group(self, id: strawberry.ID, name: str) -> ClassGroupMutationResponse:
        from core.models.core_models import ClassGroup
        name = name.strip()
        if not name:
            return ClassGroupMutationResponse(success=False, message="Name cannot be empty")
        try:
            cg = ClassGroup.objects.get(id=id)
            if ClassGroup.objects.filter(name__iexact=name).exclude(id=id).exists():
                return ClassGroupMutationResponse(success=False, message=f'"{name}" already exists')
            cg.name = name
            cg.save()
            count = Student.objects.filter(grade_level=cg.name).count()
            active = Student.objects.filter(grade_level=cg.name, status='active').count()
            return ClassGroupMutationResponse(
                success=True, message="Class group renamed",
                class_group=ClassGroupType.from_model(cg, student_count=count, active_count=active),
            )
        except ClassGroup.DoesNotExist:
            return ClassGroupMutationResponse(success=False, message="Class group not found")
