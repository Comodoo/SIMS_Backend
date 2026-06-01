"""
Core Schema
"""

from .core_schema import (
    UserType,
    StudentType,
    StaffType,
    AttendanceType,
    StudentAttendanceType,
    RegisterStudentInput,
    RegisterStaffInput,
    UpdateStudentInput,
    SelfRegisterStudentInput,
)

from .additional_core_schema import (
    RefreshTokenType,
    AuditLogType,
)

__all__ = [
    'UserType',
    'StudentType',
    'StaffType',
    'AttendanceType',
    'StudentAttendanceType',
    'RefreshTokenType',
    'AuditLogType',
]
