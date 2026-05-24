"""
HR GraphQL Schema (Strawberry)
Leave Management and Staff Attendance
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date
from hr.models.hr_models import Leave, LeaveBalance, StaffAttendanceSummary
from core.schema.core_schema import StaffType, UserType


@strawberry.type
class LeaveType:
    """GraphQL type for Leave"""
    id: strawberry.ID
    staff: StaffType
    leave_type: str
    start_date: date
    end_date: date
    total_days: int
    reason: str
    status: str
    approved_by: Optional[UserType] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    attachment_url: Optional[str] = None
    applied_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, instance: Leave):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.leave_id)),
            staff=StaffType.from_model(instance.staff),
            leave_type=instance.leave_type,
            start_date=instance.start_date,
            end_date=instance.end_date,
            total_days=instance.total_days,
            reason=instance.reason,
            status=instance.status,
            approved_by=UserType.from_model(instance.approved_by) if instance.approved_by else None,
            approved_at=instance.approved_at,
            rejection_reason=instance.rejection_reason,
            attachment_url=instance.attachment_url,
            applied_at=instance.applied_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class LeaveBalanceType:
    """GraphQL type for LeaveBalance"""
    id: strawberry.ID
    staff: StaffType
    year: int
    annual_entitlement: int
    annual_used: int
    annual_remaining: int
    sick_entitlement: int
    sick_used: int
    sick_remaining: int
    emergency_used: int
    unpaid_used: int
    updated_at: datetime
    
    @classmethod
    def from_model(cls, instance: LeaveBalance):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.balance_id)),
            staff=StaffType.from_model(instance.staff),
            year=instance.year,
            annual_entitlement=instance.annual_entitlement,
            annual_used=instance.annual_used,
            annual_remaining=instance.annual_remaining,
            sick_entitlement=instance.sick_entitlement,
            sick_used=instance.sick_used,
            sick_remaining=instance.sick_remaining,
            emergency_used=instance.emergency_used,
            unpaid_used=instance.unpaid_used,
            updated_at=instance.updated_at,
        )


@strawberry.type
class StaffAttendanceSummaryType:
    """GraphQL type for StaffAttendanceSummary"""
    id: strawberry.ID
    staff: StaffType
    year: int
    month: int
    total_work_days: int
    days_present: int
    days_absent: int
    days_late: int
    total_late_minutes: int
    average_late_minutes: float
    attendance_percentage: float
    punctuality_percentage: float
    computed_at: datetime
    
    @classmethod
    def from_model(cls, instance: StaffAttendanceSummary):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.summary_id)),
            staff=StaffType.from_model(instance.staff),
            year=instance.year,
            month=instance.month,
            total_work_days=instance.total_work_days,
            days_present=instance.days_present,
            days_absent=instance.days_absent,
            days_late=instance.days_late,
            total_late_minutes=instance.total_late_minutes,
            average_late_minutes=instance.average_late_minutes,
            attendance_percentage=instance.attendance_percentage,
            punctuality_percentage=instance.punctuality_percentage,
            computed_at=instance.computed_at,
        )


# Input Types for Mutations
@strawberry.input
class LeaveInput:
    """Input for creating Leave request"""
    staff_id: strawberry.ID
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    attachment_url: Optional[str] = None


@strawberry.input
class LeaveApprovalInput:
    """Input for approving/rejecting leave"""
    leave_id: strawberry.ID
    action: str  # 'approve' or 'reject'
    rejection_reason: Optional[str] = None


@strawberry.input
class LeaveBalanceInput:
    """Input for creating/updating LeaveBalance"""
    staff_id: strawberry.ID
    year: int
    annual_entitlement: int = 21
    sick_entitlement: int = 10


# Response Types for Mutations
@strawberry.type
class LeaveMutationResponse:
    """Response for Leave mutations"""
    success: bool
    message: str
    leave: Optional[LeaveType] = None


@strawberry.type
class LeaveBalanceMutationResponse:
    """Response for LeaveBalance mutations"""
    success: bool
    message: str
    leave_balance: Optional[LeaveBalanceType] = None
