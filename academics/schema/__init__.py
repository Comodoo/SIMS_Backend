"""
Academics Schema
"""

from .academics_schema import (
    CourseType,
    EnrollmentType,
    AssignmentType,
    SubmissionType,
)

from .academic_structure_schema import (
    DepartmentType,
    SemesterType,
)

from .grading_schema import (
    GradeComponentType,
    StudentGradeComponentType,
)

__all__ = [
    'CourseType',
    'EnrollmentType',
    'AssignmentType',
    'SubmissionType',
    'DepartmentType',
    'SemesterType',
    'GradeComponentType',
    'StudentGradeComponentType',
]
