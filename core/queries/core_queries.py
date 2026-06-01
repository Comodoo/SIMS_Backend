"""
Core GraphQL Queries (Strawberry)
"""

import strawberry
from typing import Optional, List
from django.contrib.auth import get_user_model
from core.models.core_models import User, Student, Staff, Attendance, StudentAttendance, AttendanceSession, SystemSettings
from core.schema.core_schema import (
    UserType, StudentType, StaffType, AttendanceType, StudentAttendanceType,
    AttendanceSessionType, SystemSettingType, StudentAttendanceRateType,
    ClassGroupType,
)
from core.schema.biometric_schema import BiometricStatus, EnrollmentTokenInfo
from core.schema.additional_core_schema import AuditLogType, RefreshTokenType, SecurityOverviewType
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

    @strawberry.field
    def student_by_user(self, user_id: strawberry.ID) -> Optional[StudentType]:
        """Get student profile by User ID (for logged-in student)"""
        try:
            instance = Student.objects.get(user_id=user_id)
            return StudentType.from_model(instance)
        except Student.DoesNotExist:
            return None

    @strawberry.field
    def staff_by_user(self, user_id: strawberry.ID) -> Optional[StaffType]:
        """Get staff profile by User ID (for logged-in staff)"""
        try:
            instance = Staff.objects.get(user_id=user_id)
            return StaffType.from_model(instance)
        except Staff.DoesNotExist:
            return None
    
    @strawberry.field
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
        queryset = Attendance.objects.select_related('user', 'staff__user', 'staff__department')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)
        if is_late is not None:
            queryset = queryset.filter(is_late=is_late)
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
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
        queryset = StudentAttendance.objects.select_related('student', 'course', 'marked_by__user')
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
    def attendance_sessions(
        self,
        course_id: Optional[strawberry.ID] = None,
        teacher_id: Optional[strawberry.ID] = None,
        semester_id: Optional[strawberry.ID] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AttendanceSessionType]:
        """Sessions (class meetings) — used as denominator for attendance rates."""
        qs = AttendanceSession.objects.select_related('course', 'conducted_by__user', 'semester')
        if course_id:
            qs = qs.filter(course_id=course_id)
        if teacher_id:
            qs = qs.filter(conducted_by_id=teacher_id)
        if semester_id:
            qs = qs.filter(semester_id=semester_id)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return [AttendanceSessionType.from_model(s) for s in qs[offset:offset+limit]]

    @strawberry.field
    def system_settings(self) -> List[SystemSettingType]:
        """All system settings."""
        return [SystemSettingType.from_model(s) for s in SystemSettings.objects.all()]

    @strawberry.field
    def student_attendance_by_course(
        self,
        course_id: strawberry.ID,
        date: Optional[str] = None,
        semester_id: Optional[strawberry.ID] = None,
    ) -> List[StudentAttendanceType]:
        """All attendance records for a course on a specific date (for bulk marking view)."""
        qs = StudentAttendance.objects.select_related('student', 'course', 'marked_by__user').filter(course_id=course_id)
        if date:
            qs = qs.filter(date=date)
        if semester_id:
            qs = qs.filter(semester_id=semester_id)
        return [StudentAttendanceType.from_model(r) for r in qs]

    @strawberry.field
    def student_attendance_rates(
        self,
        student_id: strawberry.ID,
        semester_id: Optional[strawberry.ID] = None,
    ) -> List[StudentAttendanceRateType]:
        """Per-course attendance rate for a student."""
        from django.db.models import Count, Q
        qs = StudentAttendance.objects.filter(student_id=student_id)
        if semester_id:
            qs = qs.filter(semester_id=semester_id)
        threshold = SystemSettings.get_int('ATTENDANCE_THRESHOLD_PERCENT', 75)
        course_ids = qs.values_list('course_id', flat=True).distinct()
        results = []
        for cid in course_ids:
            course_qs = qs.filter(course_id=cid)
            agg = course_qs.aggregate(
                total=Count('record_id'),
                present=Count('record_id', filter=Q(status='present')),
                late=Count('record_id', filter=Q(status='late')),
                absent=Count('record_id', filter=Q(status='absent')),
                excused=Count('record_id', filter=Q(status='excused')),
            )
            # Total sessions held for this course
            session_qs = AttendanceSession.objects.filter(course_id=cid, was_held=True)
            if semester_id:
                session_qs = session_qs.filter(semester_id=semester_id)
            total_sessions = session_qs.count() or agg['total']
            attended = agg['present'] + agg['late']
            rate = round(attended / total_sessions * 100, 1) if total_sessions > 0 else 0.0
            try:
                course = course_qs.first().course
            except Exception:
                continue
            results.append(StudentAttendanceRateType(
                courseId=strawberry.ID(str(cid)),
                courseName=course.name,
                totalSessions=total_sessions,
                present=agg['present'],
                late=agg['late'],
                absent=agg['absent'],
                excused=agg['excused'],
                attendanceRate=rate,
                belowThreshold=rate < threshold,
            ))
        return results

    @strawberry.field
    def staff_today_status(
        self,
        date: Optional[str] = None,
    ) -> List[AttendanceType]:
        """Latest clock-in record per staff member for a given date (defaults today)."""
        from django.utils import timezone as tz
        from django.db.models import Max
        target_date = date or tz.localdate().isoformat()
        # Get all clock-in records for today
        qs = Attendance.objects.filter(
            timestamp__date=target_date,
            status='in',
        ).select_related('user', 'staff__user', 'staff__department')
        seen = set()
        results = []
        for rec in qs.order_by('-timestamp'):
            if rec.staff_id not in seen:
                seen.add(rec.staff_id)
                results.append(AttendanceType.from_model(rec))
        return results

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
    def biometric_status(self, user_id: strawberry.ID) -> BiometricStatus:
        """Check which biometric methods are registered for a user."""
        try:
            user = User.objects.get(user_id=user_id)
            return BiometricStatus(
                has_webauthn=bool(user.webauthn_credential_id),
                has_face=bool(user.face_embedding),
                user_id=strawberry.ID(str(user.user_id)),
            )
        except User.DoesNotExist:
            return BiometricStatus(has_webauthn=False, has_face=False, user_id=strawberry.ID(str(user_id)))

    @strawberry.field
    def resolve_enrollment_token(self, token: str) -> EnrollmentTokenInfo:
        """
        Public query — no auth required.
        Resolves a magic-link enrollment token and returns the user info for the enrollment page.
        """
        from core.models.core_models import EnrollmentToken
        try:
            et = EnrollmentToken.objects.select_related('user').get(token=token)
            if not et.is_valid:
                msg = "This link has already been used." if et.used_at else "This link has expired."
                return EnrollmentTokenInfo(valid=False, message=msg)
            return EnrollmentTokenInfo(
                valid=True,
                message="Token valid",
                token=token,
                user_id=strawberry.ID(str(et.user.user_id)),
                user_name=et.user.get_full_name() or et.user.username,
                enrollment_type=et.enrollment_type,
                expires_at=et.expires_at,
            )
        except EnrollmentToken.DoesNotExist:
            return EnrollmentTokenInfo(valid=False, message="Invalid or unknown enrollment link.")

    # ------------------------------------------------------------------
    # Security — Audit Logs
    # ------------------------------------------------------------------

    @strawberry.field
    def audit_logs(
        self,
        action: Optional[str] = None,
        target_table: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AuditLogType]:
        """Return AuditLog entries with optional filters."""
        from core.models.core_models import AuditLog
        qs = AuditLog.objects.select_related('actor').order_by('-performed_at')
        if action:       qs = qs.filter(action__icontains=action)
        if target_table: qs = qs.filter(target_table=target_table)
        if date_from:    qs = qs.filter(performed_at__date__gte=date_from)
        if date_to:      qs = qs.filter(performed_at__date__lte=date_to)
        return [AuditLogType.from_model(log) for log in qs[offset:offset + limit]]

    # ------------------------------------------------------------------
    # Security — Active Sessions (non-revoked RefreshTokens)
    # ------------------------------------------------------------------

    @strawberry.field
    def active_sessions(
        self,
        limit: int = 100,
    ) -> List[RefreshTokenType]:
        """Return active (non-revoked, non-expired) refresh tokens as sessions."""
        from core.models.core_models import RefreshToken
        from django.utils import timezone as tz
        qs = RefreshToken.objects.select_related('user').filter(
            revoked=False,
            expires_at__gt=tz.now(),
        ).order_by('-issued_at')
        return [RefreshTokenType.from_model(t) for t in qs[:limit]]

    # ------------------------------------------------------------------
    # Security — Overview stats
    # ------------------------------------------------------------------

    @strawberry.field
    def class_groups(self) -> List[ClassGroupType]:
        """All class groups with live student counts."""
        from core.models.core_models import ClassGroup
        groups = ClassGroup.objects.all()
        result = []
        for g in groups:
            count = Student.objects.filter(grade_level=g.name).count()
            active = Student.objects.filter(grade_level=g.name, status='active').count()
            result.append(ClassGroupType.from_model(g, student_count=count, active_count=active))
        return result

    @strawberry.field
    def security_overview(self) -> 'SecurityOverviewType':
        """Aggregate security stats for the dashboard overview."""
        from core.models.core_models import AuditLog, RefreshToken
        from django.utils import timezone as tz
        from django.db.models import Count
        now = tz.now()
        active_sessions   = RefreshToken.objects.filter(revoked=False, expires_at__gt=now).count()
        total_users       = User.objects.filter(is_active=True).count()
        audit_total       = AuditLog.objects.count()
        return SecurityOverviewType(
            active_sessions=active_sessions,
            total_active_users=total_users,
            audit_log_total=audit_total,
        )

