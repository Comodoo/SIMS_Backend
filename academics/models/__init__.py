"""
Academics Models - Courses, Enrollment, Assignments, Submissions, Departments, Semesters, GradeComponents
"""

from .academics_models import (
    Course,
    Enrollment,
    Assignment,
    Submission,
)

from .academic_structure_models import (
    Department,
    Semester,
)

from .grading_models import (
    GradeComponent,
    StudentGradeComponent,
)

__all__ = [
    'Course',
    'Enrollment',
    'Assignment',
    'Submission',
    'Department',
    'Semester',
    'GradeComponent',
    'StudentGradeComponent',
]
