"""
Reports GraphQL Schema (Strawberry)
System Reports and Audit Logs
"""

import json
import strawberry
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from reports.models.reports_models import Report, ReportSchedule, SystemMetric
from core.models.core_models import AuditLog
from core.schema.core_schema import UserType


@strawberry.type
class ReportType:
    """GraphQL type for Report"""
    id: strawberry.ID
    title: str
    description: Optional[str] = None
    report_type: str
    format: str
    generated_by: UserType
    status: str
    parameters: Optional[str] = None  # JSON field as string
    data: Optional[str] = None  # JSON field as string
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_expired: bool
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, instance: Report):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.report_id)),
            title=instance.title,
            description=instance.description,
            report_type=instance.report_type,
            format=instance.format,
            generated_by=UserType.from_model(instance.generated_by),
            status=instance.status,
            parameters=json.dumps(instance.parameters) if instance.parameters else None,
            data=json.dumps(instance.data) if instance.data else None,
            file_url=instance.file_url,
            file_size=instance.file_size,
            generated_at=instance.generated_at,
            expires_at=instance.expires_at,
            is_expired=instance.is_expired,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class ReportScheduleType:
    """GraphQL type for ReportSchedule"""
    id: strawberry.ID
    name: str
    report_type: str
    frequency: str
    parameters: Optional[str] = None  # JSON field as string
    recipients: List[UserType]
    email_enabled: bool
    email_subject: Optional[str] = None
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_by: UserType
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, instance: ReportSchedule):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.schedule_id)),
            name=instance.name,
            report_type=instance.report_type,
            frequency=instance.frequency,
            parameters=str(instance.parameters) if instance.parameters else None,
            recipients=[UserType.from_model(user) for user in instance.recipients.all()],
            email_enabled=instance.email_enabled,
            email_subject=instance.email_subject,
            is_active=instance.is_active,
            last_run=instance.last_run,
            next_run=instance.next_run,
            created_by=UserType.from_model(instance.created_by),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class AuditLogType:
    """GraphQL type for AuditLog"""
    id: strawberry.ID
    user: Optional[UserType] = None
    action: str
    object_type: str
    object_id: Optional[str] = None
    object_repr: Optional[str] = None
    old_values: Optional[str] = None  # JSON field as string
    new_values: Optional[str] = None  # JSON field as string
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    @classmethod
    def from_model(cls, instance: AuditLog):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.log_id)),
            user=UserType.from_model(instance.user) if instance.user else None,
            action=instance.action,
            object_type=instance.object_type,
            object_id=str(instance.object_id) if instance.object_id else None,
            object_repr=instance.object_repr,
            old_values=str(instance.old_values) if instance.old_values else None,
            new_values=str(instance.new_values) if instance.new_values else None,
            ip_address=str(instance.ip_address) if instance.ip_address else None,
            user_agent=instance.user_agent,
            timestamp=instance.timestamp,
        )


@strawberry.type
class SystemMetricType:
    """GraphQL type for SystemMetric"""
    id: strawberry.ID
    name: str
    value: float
    unit: Optional[str] = None
    category: str
    metadata: Optional[str] = None  # JSON field as string
    timestamp: datetime
    
    @classmethod
    def from_model(cls, instance: SystemMetric):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.metric_id)),
            name=instance.name,
            value=instance.value,
            unit=instance.unit,
            category=instance.category,
            metadata=str(instance.metadata) if instance.metadata else None,
            timestamp=instance.timestamp,
        )


# Input Types for Mutations
@strawberry.input
class ReportInput:
    """Input for creating Report"""
    title: str
    description: Optional[str] = None
    report_type: str
    format: str = "pdf"
    parameters: Optional[str] = None
    expires_at: Optional[datetime] = None


@strawberry.input
class ReportScheduleInput:
    """Input for creating/updating ReportSchedule"""
    name: str
    report_type: str
    frequency: str
    parameters: Optional[str] = None
    recipient_ids: List[strawberry.ID]
    email_enabled: bool = True
    email_subject: Optional[str] = None
    is_active: bool = True


@strawberry.input
class SystemMetricInput:
    """Input for creating SystemMetric"""
    name: str
    value: float
    unit: Optional[str] = None
    category: str
    metadata: Optional[str] = None


# Response Types for Mutations
@strawberry.type
class ReportMutationResponse:
    """Response for Report mutations"""
    success: bool
    message: str
    report: Optional[ReportType] = None


@strawberry.type
class ReportScheduleMutationResponse:
    """Response for ReportSchedule mutations"""
    success: bool
    message: str
    schedule: Optional[ReportScheduleType] = None
