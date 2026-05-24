"""
Serializers for HR App
"""
from rest_framework import serializers
from .models import Leave, LeaveBalance, StaffAttendanceSummary


class LeaveSerializer(serializers.ModelSerializer):
    """Serializer for Leave model."""
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    staff_number = serializers.CharField(source='staff.staff_number', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    department = serializers.CharField(source='staff.department', read_only=True)
    
    class Meta:
        model = Leave
        fields = [
            'leave_id', 'staff', 'staff_name', 'staff_number', 'department',
            'leave_type', 'start_date', 'end_date', 'total_days', 'reason',
            'status', 'approved_by', 'approved_by_name', 'approved_at',
            'rejection_reason', 'attachment_url', 'applied_at', 'updated_at'
        ]
        read_only_fields = [
            'leave_id', 'total_days', 'approved_by', 'approved_at',
            'applied_at', 'updated_at'
        ]


class LeaveCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating leave requests."""
    
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'attachment_url']
    
    def validate(self, data):
        # Check start_date is before end_date
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        # Check leave balance
        staff = self.context['request'].user.staff_profile
        year = data['start_date'].year
        
        try:
            balance = LeaveBalance.objects.get(staff=staff, year=year)
            total_days = (data['end_date'] - data['start_date']).days + 1
            
            if data['leave_type'] == 'annual' and total_days > balance.annual_remaining:
                raise serializers.ValidationError(
                    f"Insufficient annual leave balance. Available: {balance.annual_remaining} days"
                )
            elif data['leave_type'] == 'sick' and total_days > balance.sick_remaining:
                raise serializers.ValidationError(
                    f"Insufficient sick leave balance. Available: {balance.sick_remaining} days"
                )
        except LeaveBalance.DoesNotExist:
            # Create balance record if not exists
            pass
        
        return data
    
    def create(self, validated_data):
        staff = self.context['request'].user.staff_profile
        return Leave.objects.create(staff=staff, **validated_data)


class LeaveApprovalSerializer(serializers.Serializer):
    """Serializer for leave approval/rejection."""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(required=False, allow_blank=True)


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Serializer for LeaveBalance model."""
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    staff_number = serializers.CharField(source='staff.staff_number', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = [
            'balance_id', 'staff', 'staff_name', 'staff_number', 'year',
            'annual_entitlement', 'annual_used', 'annual_remaining',
            'sick_entitlement', 'sick_used', 'sick_remaining',
            'emergency_used', 'unpaid_used', 'updated_at'
        ]
        read_only_fields = [
            'balance_id', 'annual_remaining', 'sick_remaining', 'updated_at'
        ]


class StaffAttendanceSummarySerializer(serializers.ModelSerializer):
    """Serializer for StaffAttendanceSummary model."""
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    staff_number = serializers.CharField(source='staff.staff_number', read_only=True)
    department = serializers.CharField(source='staff.department', read_only=True)
    
    class Meta:
        model = StaffAttendanceSummary
        fields = [
            'summary_id', 'staff', 'staff_name', 'staff_number', 'department',
            'year', 'month', 'total_work_days', 'days_present', 'days_absent',
            'days_late', 'total_late_minutes', 'average_late_minutes',
            'attendance_percentage', 'punctuality_percentage', 'computed_at'
        ]
        read_only_fields = ['summary_id', 'computed_at']
