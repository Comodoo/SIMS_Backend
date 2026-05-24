"""
HR GraphQL Queries (Strawberry)
"""

import strawberry
from typing import Optional, List
from hr.models.hr_models import Leave, LeaveBalance, StaffAttendanceSummary
from hr.schema.hr_schema import LeaveType, LeaveBalanceType, StaffAttendanceSummaryType


@strawberry.type
class HrQuery:
    """GraphQL queries for HR module"""
    
    @strawberry.field
    def leaves(
        self,
        staff_id: Optional[strawberry.ID] = None,
        leave_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LeaveType]:
        """Query leave requests with filters"""
        queryset = Leave.objects.all()
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)
        if status:
            queryset = queryset.filter(status=status)
        return [LeaveType.from_model(leave) for leave in queryset[offset:offset+limit]]
    
    @strawberry.field
    def leave(self, id: strawberry.ID) -> Optional[LeaveType]:
        """Get leave request by ID"""
        try:
            instance = Leave.objects.get(leave_id=id)
            return LeaveType.from_model(instance)
        except Leave.DoesNotExist:
            return None
    
    @strawberry.field
    def leave_balances(
        self,
        staff_id: Optional[strawberry.ID] = None,
        year: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LeaveBalanceType]:
        """Query leave balances with filters"""
        queryset = LeaveBalance.objects.all()
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        if year:
            queryset = queryset.filter(year=year)
        return [LeaveBalanceType.from_model(balance) for balance in queryset[offset:offset+limit]]
    
    @strawberry.field
    def staff_attendance_summaries(
        self,
        staff_id: Optional[strawberry.ID] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[StaffAttendanceSummaryType]:
        """Query staff attendance summaries with filters"""
        queryset = StaffAttendanceSummary.objects.all()
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)
        return [StaffAttendanceSummaryType.from_model(summary) for summary in queryset[offset:offset+limit]]
