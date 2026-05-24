"""
Grading GraphQL Schema Types - GradeComponents, StudentGradeComponents
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from academics.models.grading_models import GradeComponent, StudentGradeComponent


@strawberry.type
class GradeComponentType:
    """GraphQL type for GradeComponent"""
    id: strawberry.ID
    course_id: strawberry.ID
    name: str
    weight_percent: float
    max_score: float
    due_date: Optional[str]
    type: str
    
    @classmethod
    def from_model(cls, component: GradeComponent) -> 'GradeComponentType':
        return cls(
            id=str(component.component_id),
            course_id=str(component.course.course_id),
            name=component.name,
            weight_percent=component.weight_percent,
            max_score=component.max_score,
            due_date=component.due_date.isoformat() if component.due_date else None,
            type=component.type,
        )


@strawberry.type
class StudentGradeComponentType:
    """GraphQL type for StudentGradeComponent"""
    id: strawberry.ID
    enrollment_id: strawberry.ID
    component_id: strawberry.ID
    score: Optional[float]
    graded_by_id: Optional[strawberry.ID]
    graded_at: Optional[str]
    remarks: Optional[str]
    
    @classmethod
    def from_model(cls, sgc: StudentGradeComponent) -> 'StudentGradeComponentType':
        return cls(
            id=str(sgc.sgc_id),
            enrollment_id=str(sgc.enrollment.enrollment_id),
            component_id=str(sgc.component.component_id),
            score=sgc.score,
            graded_by_id=str(sgc.graded_by.staff_id) if sgc.graded_by else None,
            graded_at=sgc.graded_at.isoformat() if sgc.graded_at else None,
            remarks=sgc.remarks,
        )


# Input Types
@strawberry.input
class GradeComponentInput:
    """Input for creating GradeComponent"""
    course_id: strawberry.ID
    name: str
    weight_percent: float
    max_score: float = 100.0
    due_date: Optional[str] = None
    type: str


@strawberry.input
class StudentGradeComponentInput:
    """Input for creating StudentGradeComponent"""
    enrollment_id: strawberry.ID
    component_id: strawberry.ID
    score: Optional[float] = None
    remarks: Optional[str] = None
