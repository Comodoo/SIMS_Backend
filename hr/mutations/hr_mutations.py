"""
HR GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional
from django.utils import timezone
from hr.models.hr_models import Leave, LeaveBalance, StaffAttendanceSummary
from hr.schema.hr_schema import LeaveType, LeaveBalanceType, StaffAttendanceSummaryType, LeaveInput, LeaveApprovalInput, LeaveBalanceInput


@strawberry.type
class HrMutationResponse:
    """Response type for HR mutations"""
    success: bool
    message: str


@strawberry.type
class LeaveMutationResponse(HrMutationResponse):
    """Response type for leave mutations"""
    leave: Optional[LeaveType] = None


def _error_response(message: str) -> HrMutationResponse:
    """Helper for error responses"""
    return HrMutationResponse(success=False, message=message)


@strawberry.type
class HrMutation:
    """GraphQL mutations for HR module"""
    
    @strawberry.mutation
    def create_leave_request(self, input: LeaveInput) -> LeaveMutationResponse:
        """Create a new leave request"""
        try:
            leave = Leave.objects.create(
                staff_id=input.staff_id,
                leave_type=input.leave_type,
                start_date=input.start_date,
                end_date=input.end_date,
                reason=input.reason,
                attachment_url=input.attachment_url
            )
            
            return LeaveMutationResponse(
                success=True, 
                message="Leave request created successfully", 
                leave=LeaveType.from_model(leave)
            )
        except Exception as e:
            return LeaveMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def approve_leave(self, leave_id: strawberry.ID, approved_by_id: strawberry.ID) -> LeaveMutationResponse:
        """Approve a leave request"""
        try:
            from core.models.core_models import User
            leave = Leave.objects.get(leave_id=leave_id)
            approver = User.objects.get(user_id=approved_by_id)
            leave.approve(approved_by_user=approver)
            
            return LeaveMutationResponse(
                success=True, 
                message="Leave request approved successfully", 
                leave=LeaveType.from_model(leave)
            )
        except Leave.DoesNotExist:
            return LeaveMutationResponse(success=False, message="Leave request not found")
        except User.DoesNotExist:
            return LeaveMutationResponse(success=False, message="Approver not found")
        except Exception as e:
            return LeaveMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def reject_leave(self, leave_id: strawberry.ID, rejection_reason: str, rejected_by_id: strawberry.ID) -> LeaveMutationResponse:
        """Reject a leave request"""
        try:
            from core.models.core_models import User
            leave = Leave.objects.get(leave_id=leave_id)
            rejecter = User.objects.get(user_id=rejected_by_id)
            leave.reject(reason=rejection_reason, rejected_by_user=rejecter)
            
            return LeaveMutationResponse(
                success=True, 
                message="Leave request rejected successfully", 
                leave=LeaveType.from_model(leave)
            )
        except Leave.DoesNotExist:
            return LeaveMutationResponse(success=False, message="Leave request not found")
        except User.DoesNotExist:
            return LeaveMutationResponse(success=False, message="Rejecter not found")
        except Exception as e:
            return LeaveMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_leave_balance(self, input: LeaveBalanceInput) -> HrMutationResponse:
        """Create leave balance for staff member"""
        try:
            balance = LeaveBalance.objects.create(
                staff_id=input.staff_id,
                year=input.year,
                annual_entitlement=input.annual_entitlement or 21,
                sick_entitlement=input.sick_entitlement or 10
            )
            
            return HrMutationResponse(success=True, message="Leave balance created successfully")
        except Exception as e:
            return HrMutationResponse(success=False, message=f"Error: {str(e)}")
