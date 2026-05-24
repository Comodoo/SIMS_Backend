"""
Academics Mutations
"""

from .academics_mutations import AcademicsMutation
from .academic_structure_mutations import DepartmentMutations, SemesterMutations
from .grading_mutations import GradeComponentMutations, StudentGradeComponentMutations

__all__ = [
    'AcademicsMutation',
    'DepartmentMutations',
    'SemesterMutations',
    'GradeComponentMutations',
    'StudentGradeComponentMutations',
]
