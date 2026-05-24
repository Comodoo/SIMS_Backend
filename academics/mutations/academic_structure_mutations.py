"""
Academic Structure GraphQL Mutations - Departments, Semesters
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from academics.models.academic_structure_models import Department, Semester
from academics.schema.academic_structure_schema import DepartmentType, SemesterType, DepartmentInput, SemesterInput
from core.models.core_models import Staff


# Response Types
@strawberry.type
class DepartmentResponse:
    """Response for Department mutations"""
    success: bool
    message: str
    department: Optional[DepartmentType] = None


@strawberry.type
class SemesterResponse:
    """Response for Semester mutations"""
    success: bool
    message: str
    semester: Optional[SemesterType] = None


# Mutations
@strawberry.type
class DepartmentMutations:
    """Mutations for Department"""
    
    @strawberry.mutation
    def create_department(self, input: DepartmentInput) -> DepartmentResponse:
        """Create a new department"""
        try:
            hod = None
            if input.hod_id:
                hod = Staff.objects.get(staff_id=str(input.hod_id))
            
            department = Department.objects.create(
                name=input.name,
                code=input.code,
                hod=hod,
                description=input.description,
                is_active=input.is_active,
            )
            
            return DepartmentResponse(
                success=True,
                message="Department created successfully",
                department=DepartmentType.from_model(department),
            )
        except Staff.DoesNotExist:
            return DepartmentResponse(
                success=False,
                message="HOD (Staff) not found",
            )
        except Exception as e:
            return DepartmentResponse(
                success=False,
                message=f"Error creating department: {str(e)}",
            )
    
    @strawberry.mutation
    def update_department(self, dept_id: strawberry.ID, input: DepartmentInput) -> DepartmentResponse:
        """Update an existing department"""
        try:
            department = Department.objects.get(dept_id=str(dept_id))
            
            hod = None
            if input.hod_id:
                hod = Staff.objects.get(staff_id=str(input.hod_id))
            
            department.name = input.name
            department.code = input.code
            department.hod = hod
            department.description = input.description
            department.is_active = input.is_active
            department.save()
            
            return DepartmentResponse(
                success=True,
                message="Department updated successfully",
                department=DepartmentType.from_model(department),
            )
        except Department.DoesNotExist:
            return DepartmentResponse(
                success=False,
                message="Department not found",
            )
        except Staff.DoesNotExist:
            return DepartmentResponse(
                success=False,
                message="HOD (Staff) not found",
            )
        except Exception as e:
            return DepartmentResponse(
                success=False,
                message=f"Error updating department: {str(e)}",
            )
    
    @strawberry.mutation
    def delete_department(self, dept_id: strawberry.ID) -> DepartmentResponse:
        """Delete a department (soft delete by setting is_active=False)"""
        try:
            department = Department.objects.get(dept_id=str(dept_id))
            department.is_active = False
            department.save()
            
            return DepartmentResponse(
                success=True,
                message="Department deleted successfully",
                department=DepartmentType.from_model(department),
            )
        except Department.DoesNotExist:
            return DepartmentResponse(
                success=False,
                message="Department not found",
            )
        except Exception as e:
            return DepartmentResponse(
                success=False,
                message=f"Error deleting department: {str(e)}",
            )


@strawberry.type
class SemesterMutations:
    """Mutations for Semester"""
    
    @strawberry.mutation
    def create_semester(self, input: SemesterInput) -> SemesterResponse:
        """Create a new semester"""
        try:
            from datetime import datetime
            
            semester = Semester.objects.create(
                name=input.name,
                academic_year=input.academic_year,
                start_date=datetime.fromisoformat(input.start_date).date(),
                end_date=datetime.fromisoformat(input.end_date).date(),
                enrollment_open=datetime.fromisoformat(input.enrollment_open).date(),
                enrollment_close=datetime.fromisoformat(input.enrollment_close).date(),
                status=input.status,
            )
            
            return SemesterResponse(
                success=True,
                message="Semester created successfully",
                semester=SemesterType.from_model(semester),
            )
        except Exception as e:
            return SemesterResponse(
                success=False,
                message=f"Error creating semester: {str(e)}",
            )
    
    @strawberry.mutation
    def update_semester(self, semester_id: strawberry.ID, input: SemesterInput) -> SemesterResponse:
        """Update an existing semester"""
        try:
            from datetime import datetime
            
            semester = Semester.objects.get(semester_id=str(semester_id))
            
            semester.name = input.name
            semester.academic_year = input.academic_year
            semester.start_date = datetime.fromisoformat(input.start_date).date()
            semester.end_date = datetime.fromisoformat(input.end_date).date()
            semester.enrollment_open = datetime.fromisoformat(input.enrollment_open).date()
            semester.enrollment_close = datetime.fromisoformat(input.enrollment_close).date()
            semester.status = input.status
            semester.save()
            
            return SemesterResponse(
                success=True,
                message="Semester updated successfully",
                semester=SemesterType.from_model(semester),
            )
        except Semester.DoesNotExist:
            return SemesterResponse(
                success=False,
                message="Semester not found",
            )
        except Exception as e:
            return SemesterResponse(
                success=False,
                message=f"Error updating semester: {str(e)}",
            )
