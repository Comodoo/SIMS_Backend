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
