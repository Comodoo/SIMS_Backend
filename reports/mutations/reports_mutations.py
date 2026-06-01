"""
Reports GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional
from django.utils import timezone
from reports.models.reports_models import Report, ReportSchedule, SystemMetric
from reports.schema.reports_schema import ReportType, ReportScheduleType, SystemMetricType, ReportInput, ReportScheduleInput, SystemMetricInput


@strawberry.type
class ReportsMutationResponse:
    """Response type for reports mutations"""
    success: bool
    message: str


@strawberry.type
class ReportMutationResponse(ReportsMutationResponse):
    """Response type for report mutations"""
    report: Optional[ReportType] = None


@strawberry.type
class ReportScheduleMutationResponse(ReportsMutationResponse):
    """Response type for report schedule mutations"""
    schedule: Optional[ReportScheduleType] = None


def _error_response(message: str) -> ReportsMutationResponse:
    """Helper for error responses"""
    return ReportsMutationResponse(success=False, message=message)


@strawberry.type
class ReportsMutation:
    """GraphQL mutations for Reports module"""
    
    @strawberry.mutation
    def create_report(self, input: ReportInput, generated_by_id: strawberry.ID) -> ReportMutationResponse:
        """Create a new report"""
        try:
            from core.models.core_models import User
            user = User.objects.get(user_id=generated_by_id)
            
            report = Report.objects.create(
                title=input.title,
                description=input.description,
                report_type=input.report_type,
                format=input.format or 'pdf',
                generated_by=user,
                parameters=input.parameters,
                expires_at=input.expires_at
            )
            
            return ReportMutationResponse(
                success=True, 
                message="Report created successfully", 
                report=ReportType.from_model(report)
            )
        except User.DoesNotExist:
            return ReportMutationResponse(success=False, message="User not found")
        except Exception as e:
            return ReportMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def generate_report(self, report_id: strawberry.ID) -> ReportMutationResponse:
        """Generate a report (mark as completed)"""
        try:
            report = Report.objects.get(report_id=report_id)
            report.status = 'generating'
            report.save()
            
            # Simulate report generation (in real implementation, this would be a background task)
            report.status = 'completed'
            report.generated_at = timezone.now()
            report.file_url = f"/media/reports/{report.title.replace(' ', '_')}.pdf"
            report.file_size = 1024000  # 1MB
            report.save()
            
            return ReportMutationResponse(
                success=True, 
                message="Report generated successfully", 
                report=ReportType.from_model(report)
            )
        except Report.DoesNotExist:
            return ReportMutationResponse(success=False, message="Report not found")
        except Exception as e:
            return ReportMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_report_schedule(self, input: ReportScheduleInput, created_by_id: strawberry.ID) -> ReportScheduleMutationResponse:
        """Create a new report schedule"""
        try:
            from core.models.core_models import User
            user = User.objects.get(user_id=created_by_id)
            
            schedule = ReportSchedule.objects.create(
                name=input.name,
                report_type=input.report_type,
                frequency=input.frequency,
                parameters=input.parameters,
                email_enabled=input.email_enabled or True,
                email_subject=input.email_subject,
                is_active=input.is_active or True,
                created_by=user
            )
            
            # Add recipients
            if input.recipient_ids:
                schedule.recipients.set(input.recipient_ids)
            
            return ReportScheduleMutationResponse(
                success=True, 
                message="Report schedule created successfully", 
                schedule=ReportScheduleType.from_model(schedule)
            )
        except User.DoesNotExist:
            return ReportScheduleMutationResponse(success=False, message="User not found")
        except Exception as e:
            return ReportScheduleMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_system_metric(self, input: SystemMetricInput) -> ReportsMutationResponse:
        """Create a new system metric"""
        try:
            metric = SystemMetric.objects.create(
                name=input.name,
                value=input.value,
                unit=input.unit,
                category=input.category,
                metadata=input.metadata
            )
            
            return ReportsMutationResponse(success=True, message="System metric created successfully")
        except Exception as e:
            return ReportsMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def generate_system_report(
        self,
        report_type: str,
        generated_by_id: strawberry.ID,
        title: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        semester_id: Optional[strawberry.ID] = None,
        course_id: Optional[strawberry.ID] = None,
    ) -> ReportMutationResponse:
        """
        Generate a real data report from the database and store it as JSON.
        Supported types: attendance | staff_attendance | grades | enrollment
        """
        try:
            from core.models.core_models import User
            user = User.objects.get(user_id=generated_by_id)

            auto_title = title or f"{report_type.replace('_', ' ').title()} Report — {timezone.now().strftime('%d %b %Y')}"

            report = Report.objects.create(
                title=auto_title,
                report_type=report_type,
                format='json',
                generated_by=user,
                status='generating',
                parameters={
                    'date_from': date_from,
                    'date_to': date_to,
                    'semester_id': str(semester_id) if semester_id else None,
                    'course_id': str(course_id) if course_id else None,
                },
            )

            data: dict = {}

            if report_type == 'attendance':
                from core.models.core_models import StudentAttendance
                qs = StudentAttendance.objects.select_related(
                    'student__user', 'course', 'marked_by__user'
                )
                if date_from:   qs = qs.filter(date__gte=date_from)
                if date_to:     qs = qs.filter(date__lte=date_to)
                if semester_id: qs = qs.filter(semester_id=semester_id)
                if course_id:   qs = qs.filter(course_id=course_id)
                records = []
                for r in qs.order_by('course__name', 'date', 'student__student_number'):
                    records.append({
                        'student':        r.student.full_name,
                        'student_number': r.student.student_number,
                        'course':         r.course.name,
                        'course_code':    r.course.course_code,
                        'date':           str(r.date),
                        'status':         r.status,
                        'method':         r.method,
                        'marked_by':      r.marked_by.user.get_full_name() if r.marked_by else '—',
                    })
                data = {'columns': ['student', 'student_number', 'course', 'course_code', 'date', 'status', 'method', 'marked_by'],
                        'records': records, 'total': len(records)}

            elif report_type == 'staff_attendance':
                from core.models.core_models import Attendance
                from datetime import datetime as dt
                qs = Attendance.objects.select_related('user', 'staff')
                if date_from:
                    qs = qs.filter(timestamp__gte=dt.strptime(date_from, '%Y-%m-%d'))
                if date_to:
                    qs = qs.filter(timestamp__lte=dt.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
                records = []
                for r in qs.order_by('-timestamp'):
                    records.append({
                        'name':         r.user.get_full_name() or r.user.username,
                        'role':         r.user.role,
                        'position':     r.staff.position if r.staff else '—',
                        'date':         str(r.timestamp.date()),
                        'time':         r.timestamp.strftime('%H:%M'),
                        'status':       r.status,
                        'late':         'Yes' if r.is_late else 'No',
                        'late_minutes': r.late_minutes or 0,
                        'method':       r.method,
                    })
                data = {'columns': ['name', 'role', 'position', 'date', 'time', 'status', 'late', 'late_minutes', 'method'],
                        'records': records, 'total': len(records)}

            elif report_type in ('grades', 'results'):
                from academics.models.grading_models import ResultCard
                qs = ResultCard.objects.select_related('student__user', 'subject', 'semester')
                if semester_id: qs = qs.filter(semester_id=semester_id)
                if course_id:   qs = qs.filter(subject_id=course_id)
                records = []
                for r in qs.order_by('subject__name', 'student__student_number'):
                    records.append({
                        'student':        r.student.full_name,
                        'student_number': r.student.student_number,
                        'subject':        r.subject.name,
                        'course_code':    r.subject.course_code,
                        'semester':       r.semester.name,
                        'cat1':           float(r.cat1_score) if r.cat1_score is not None else '—',
                        'cat2':           float(r.cat2_score) if r.cat2_score is not None else '—',
                        'exam':           float(r.exam_score) if r.exam_score is not None else '—',
                        'total':          float(r.total_score) if r.total_score is not None else '—',
                        'grade':          r.grade_letter or '—',
                        'remarks':        r.remarks or '—',
                    })
                data = {'columns': ['student', 'student_number', 'subject', 'course_code', 'semester', 'cat1', 'cat2', 'exam', 'total', 'grade', 'remarks'],
                        'records': records, 'total': len(records)}

            elif report_type == 'enrollment':
                from academics.models.academics_models import Enrollment
                qs = Enrollment.objects.select_related('student__user', 'course', 'semester')
                if semester_id: qs = qs.filter(semester_id=semester_id)
                if course_id:   qs = qs.filter(course_id=course_id)
                records = []
                for r in qs.order_by('course__name', 'student__student_number'):
                    records.append({
                        'student':        r.student.full_name,
                        'student_number': r.student.student_number,
                        'course':         r.course.name,
                        'course_code':    r.course.course_code,
                        'semester':       r.semester.name if r.semester else '—',
                        'status':         r.status,
                        'enrolled_at':    str(r.enrolled_at.date()) if r.enrolled_at else '—',
                    })
                data = {'columns': ['student', 'student_number', 'course', 'course_code', 'semester', 'status', 'enrolled_at'],
                        'records': records, 'total': len(records)}

            else:
                data = {'columns': [], 'records': [], 'total': 0}

            report.data = data
            report.status = 'completed'
            report.generated_at = timezone.now()
            report.save()

            return ReportMutationResponse(
                success=True,
                message=f"Report generated — {data.get('total', 0)} records",
                report=ReportType.from_model(report),
            )
        except Exception as e:
            if 'report' in dir():
                try:
                    report.status = 'failed'
                    report.save()
                except Exception:
                    pass
            return ReportMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def delete_report(self, report_id: strawberry.ID) -> ReportsMutationResponse:
        """Delete a report"""
        try:
            report = Report.objects.get(report_id=report_id)
            report.delete()
            
            return ReportsMutationResponse(success=True, message="Report deleted successfully")
        except Report.DoesNotExist:
            return ReportsMutationResponse(success=False, message="Report not found")
        except Exception as e:
            return ReportsMutationResponse(success=False, message=f"Error: {str(e)}")
