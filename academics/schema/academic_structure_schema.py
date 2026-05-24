"""
Academic Structure GraphQL Schema Types - Departments, Semesters
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from academics.models.academic_structure_models import Department, Semester


@strawberry.type
class DepartmentType:
    """GraphQL type for Department"""
    id: strawberry.ID
    name: str
    code: str
    hod_id: Optional[strawberry.ID]
    description: Optional[str]
    is_active: bool
    created_at: str
    
    @classmethod
    def from_model(cls, dept: Department) -> 'DepartmentType':
        return cls(
            id=str(dept.dept_id),
            name=dept.name,
            code=dept.code,
            hod_id=str(dept.hod.staff_id) if dept.hod else None,
            description=dept.description,
            is_active=dept.is_active,
            created_at=dept.created_at.isoformat(),
        )


@strawberry.type
class SemesterType:
    """GraphQL type for Semester"""
    id: strawberry.ID
    name: str
    academic_year: str
    start_date: str
    end_date: str
    enrollment_open: str
    enrollment_close: str
    status: str
    
    @classmethod
    def from_model(cls, semester: Semester) -> 'SemesterType':
        return cls(
            id=str(semester.semester_id),
            name=semester.name,
            academic_year=semester.academic_year,
            start_date=semester.start_date.isoformat(),
            end_date=semester.end_date.isoformat(),
            enrollment_open=semester.enrollment_open.isoformat(),
            enrollment_close=semester.enrollment_close.isoformat(),
            status=semester.status,
        )


# Input Types
@strawberry.input
class DepartmentInput:
    """Input for creating Department"""
    name: str
    code: str
    hod_id: Optional[strawberry.ID] = None
    description: Optional[str] = None
    is_active: bool = True


@strawberry.input
class SemesterInput:
    """Input for creating Semester"""
    name: str
    academic_year: str
    start_date: str
    end_date: str
    enrollment_open: str
    enrollment_close: str
    status: str = 'upcoming'
