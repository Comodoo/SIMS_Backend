"""
Grading GraphQL Mutations - GradeComponents, StudentGradeComponents
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from academics.models.grading_models import GradeComponent, StudentGradeComponent
from academics.models.academics_models import Course, Enrollment
from academics.schema.grading_schema import GradeComponentType, StudentGradeComponentType, GradeComponentInput, StudentGradeComponentInput
from core.models.core_models import Staff


# Response Types
@strawberry.type
class GradeComponentResponse:
    """Response for GradeComponent mutations"""
    success: bool
    message: str
    component: Optional[GradeComponentType] = None


@strawberry.type
class StudentGradeComponentResponse:
    """Response for StudentGradeComponent mutations"""
    success: bool
    message: str
    grade_component: Optional[StudentGradeComponentType] = None


# Mutations
@strawberry.type
class GradeComponentMutations:
    """Mutations for GradeComponent"""
    
    @strawberry.mutation
    def create_grade_component(self, input: GradeComponentInput) -> GradeComponentResponse:
        """Create a new grade component for a course"""
        try:
            from datetime import datetime
            
            course = Course.objects.get(course_id=str(input.course_id))
            
            due_date = None
            if input.due_date:
                due_date = datetime.fromisoformat(input.due_date).date()
            
            component = GradeComponent.objects.create(
                course=course,
                name=input.name,
                weight_percent=input.weight_percent,
                max_score=input.max_score,
                due_date=due_date,
                type=input.type,
            )
            
            return GradeComponentResponse(
                success=True,
                message="Grade component created successfully",
                component=GradeComponentType.from_model(component),
            )
        except Course.DoesNotExist:
            return GradeComponentResponse(
                success=False,
                message="Course not found",
            )
        except Exception as e:
            return GradeComponentResponse(
                success=False,
                message=f"Error creating grade component: {str(e)}",
            )
    
    @strawberry.mutation
    def update_grade_component(self, component_id: strawberry.ID, input: GradeComponentInput) -> GradeComponentResponse:
        """Update an existing grade component"""
        try:
            from datetime import datetime
            
            component = GradeComponent.objects.get(component_id=str(component_id))
            course = Course.objects.get(course_id=str(input.course_id))
            
            due_date = None
            if input.due_date:
                due_date = datetime.fromisoformat(input.due_date).date()
            
            component.course = course
            component.name = input.name
            component.weight_percent = input.weight_percent
            component.max_score = input.max_score
            component.due_date = due_date
            component.type = input.type
            component.save()
            
            return GradeComponentResponse(
                success=True,
                message="Grade component updated successfully",
                component=GradeComponentType.from_model(component),
            )
        except GradeComponent.DoesNotExist:
            return GradeComponentResponse(
                success=False,
                message="Grade component not found",
            )
        except Course.DoesNotExist:
            return GradeComponentResponse(
                success=False,
                message="Course not found",
            )
        except Exception as e:
            return GradeComponentResponse(
                success=False,
                message=f"Error updating grade component: {str(e)}",
            )
    
    @strawberry.mutation
    def delete_grade_component(self, component_id: strawberry.ID) -> GradeComponentResponse:
        """Delete a grade component"""
        try:
            component = GradeComponent.objects.get(component_id=str(component_id))
            component.delete()
            
            return GradeComponentResponse(
                success=True,
                message="Grade component deleted successfully",
            )
        except GradeComponent.DoesNotExist:
            return GradeComponentResponse(
                success=False,
                message="Grade component not found",
            )
        except Exception as e:
            return GradeComponentResponse(
                success=False,
                message=f"Error deleting grade component: {str(e)}",
            )


@strawberry.type
class StudentGradeComponentMutations:
    """Mutations for StudentGradeComponent"""
    
    @strawberry.mutation
    def create_student_grade_component(self, input: StudentGradeComponentInput, graded_by_id: strawberry.ID) -> StudentGradeComponentResponse:
        """Create or update a student's grade for a component"""
        try:
            from django.utils import timezone
            
            enrollment = Enrollment.objects.get(enrollment_id=str(input.enrollment_id))
            component = GradeComponent.objects.get(component_id=str(input.component_id))
            graded_by = Staff.objects.get(staff_id=str(graded_by_id))
            
            # Check if already exists, update if so
            sgc, created = StudentGradeComponent.objects.update_or_create(
                enrollment=enrollment,
                component=component,
                defaults={
                    'score': input.score,
                    'graded_by': graded_by,
                    'graded_at': timezone.now(),
                    'remarks': input.remarks,
                }
            )
            
            return StudentGradeComponentResponse(
                success=True,
                message=f"Student grade component {'created' if created else 'updated'} successfully",
                grade_component=StudentGradeComponentType.from_model(sgc),
            )
        except Enrollment.DoesNotExist:
            return StudentGradeComponentResponse(
                success=False,
                message="Enrollment not found",
            )
        except GradeComponent.DoesNotExist:
            return StudentGradeComponentResponse(
                success=False,
                message="Grade component not found",
            )
        except Staff.DoesNotExist:
            return StudentGradeComponentResponse(
                success=False,
                message="Staff (grader) not found",
            )
        except Exception as e:
            return StudentGradeComponentResponse(
                success=False,
                message=f"Error creating student grade component: {str(e)}",
            )
