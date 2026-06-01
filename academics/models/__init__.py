"""
Academics Models - Courses/Subjects, Enrollment, Assignments, Submissions,
Departments, Semesters, GradeComponents, SubjectTeacher, Timetable, ResultCard
"""

from .academics_models import (
    Course,
    Enrollment,
    Assignment,
    Submission,
    SubjectTeacher,
    Timetable,
)

from .academic_structure_models import (
    Department,
    Semester,
)

from .grading_models import (
    GradeComponent,
    StudentGradeComponent,
    ResultCard,
)

__all__ = [
    'Course',
    'Enrollment',
    'Assignment',
    'Submission',
    'SubjectTeacher',
    'Timetable',
    'Department',
    'Semester',
    'GradeComponent',
    'StudentGradeComponent',
    'ResultCard',
]
