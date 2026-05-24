"""
Reports GraphQL Queries (Strawberry)
"""

import strawberry
from typing import Optional, List
from reports.models.reports_models import Report, ReportSchedule, SystemMetric
from core.models.core_models import AuditLog
from reports.schema.reports_schema import ReportType, ReportScheduleType, AuditLogType, SystemMetricType


@strawberry.type
class ReportsQuery:
    """GraphQL queries for Reports module"""
    
    @strawberry.field
    def reports(
        self,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        generated_by_id: Optional[strawberry.ID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ReportType]:
        """Query reports with filters"""
        queryset = Report.objects.all()
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if status:
            queryset = queryset.filter(status=status)
        if generated_by_id:
            queryset = queryset.filter(generated_by_id=generated_by_id)
        return [ReportType.from_model(report) for report in queryset[offset:offset+limit]]
    
    @strawberry.field
    def report(self, id: strawberry.ID) -> Optional[ReportType]:
        """Get report by ID"""
        try:
            instance = Report.objects.get(report_id=id)
            return ReportType.from_model(instance)
        except Report.DoesNotExist:
            return None
    
    @strawberry.field
    def report_schedules(
        self,
        report_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ReportScheduleType]:
        """Query report schedules with filters"""
        queryset = ReportSchedule.objects.all()
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return [ReportScheduleType.from_model(schedule) for schedule in queryset[offset:offset+limit]]
    
    @strawberry.field
    def report_schedule(self, id: strawberry.ID) -> Optional[ReportScheduleType]:
        """Get report schedule by ID"""
        try:
            instance = ReportSchedule.objects.get(schedule_id=id)
            return ReportScheduleType.from_model(instance)
        except ReportSchedule.DoesNotExist:
            return None
    
    @strawberry.field
    def audit_logs(
        self,
        user_id: Optional[strawberry.ID] = None,
        action: Optional[str] = None,
        object_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLogType]:
        """Query audit logs with filters"""
        queryset = AuditLog.objects.all()
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        if object_type:
            queryset = queryset.filter(object_type=object_type)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        return [AuditLogType.from_model(log) for log in queryset[offset:offset+limit]]
    
    @strawberry.field
    def system_metrics(
        self,
        category: Optional[str] = None,
        name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SystemMetricType]:
        """Query system metrics with filters"""
        queryset = SystemMetric.objects.all()
        if category:
            queryset = queryset.filter(category=category)
        if name:
            queryset = queryset.filter(name=name)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        return [SystemMetricType.from_model(metric) for metric in queryset[offset:offset+limit]]
