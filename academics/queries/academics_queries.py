"""
Academics GraphQL Queries (Strawberry)
"""

import strawberry
from typing import Optional, List
from academics.models.academics_models import Course, Enrollment, Assignment, Submission, SubjectTeacher, Timetable
from academics.models.grading_models import ResultCard
from academics.schema.academics_schema import (
    CourseType, EnrollmentType, AssignmentType, SubmissionType,
    SubjectTeacherType, TimetableType, ResultCardType,
)


@strawberry.type
class AcademicsQuery:
    """GraphQL queries for Academics module"""
    
    @strawberry.field
    def courses(
        self,
        status: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[CourseType]:
        """Query courses with filters"""
        queryset = Course.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        if department:
            queryset = queryset.filter(department=department)
        return [CourseType.from_model(course) for course in queryset[offset:offset+limit]]
    
    @strawberry.field
    def course(self, id: strawberry.ID) -> Optional[CourseType]:
        """Get course by ID"""
        try:
            instance = Course.objects.get(course_id=id)
            return CourseType.from_model(instance)
        except Course.DoesNotExist:
            return None
    
    @strawberry.field
    def enrollments(
        self,
        student_id: Optional[strawberry.ID] = None,
        course_id: Optional[strawberry.ID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[EnrollmentType]:
        """Query enrollments with filters"""
        queryset = Enrollment.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if status:
            queryset = queryset.filter(status=status)
        return [EnrollmentType.from_model(enrollment) for enrollment in queryset[offset:offset+limit]]
    
    @strawberry.field
    def assignments(
        self,
        course_id: Optional[strawberry.ID] = None,
        assignment_type: Optional[str] = None,
        is_published: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssignmentType]:
        """Query assignments with filters"""
        queryset = Assignment.objects.all()
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if assignment_type:
            queryset = queryset.filter(assignment_type=assignment_type)
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published)
        return [AssignmentType.from_model(assignment) for assignment in queryset[offset:offset+limit]]
    
    @strawberry.field
    def submissions(
        self,
        student_id: Optional[strawberry.ID] = None,
        assignment_id: Optional[strawberry.ID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SubmissionType]:
        """Query submissions with filters"""
        queryset = Submission.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        if status:
            queryset = queryset.filter(status=status)
        return [SubmissionType.from_model(sub) for sub in queryset[offset:offset+limit]]

    @strawberry.field
    def departments(self) -> List["DepartmentType"]:
        """Query all departments"""
        from academics.models.academic_structure_models import Department
        from academics.schema.academics_schema import DepartmentType
        return [DepartmentType.from_model(dept) for dept in Department.objects.all()]

    @strawberry.field
    def semesters(self) -> List["SemesterType"]:
        """Query all semesters"""
        from academics.models.academic_structure_models import Semester
        from academics.schema.academics_schema import SemesterType
        return [SemesterType.from_model(sem) for sem in Semester.objects.all()]

    # --- New queries: SubjectTeacher, Timetable, ResultCard ---

    @strawberry.field
    def subject_teachers(
        self,
        subject_id: Optional[strawberry.ID] = None,
        teacher_id: Optional[strawberry.ID] = None,
    ) -> List[SubjectTeacherType]:
        """Get all teacher-subject assignments, optionally filtered."""
        qs = SubjectTeacher.objects.select_related('subject', 'teacher', 'teacher__user')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return [SubjectTeacherType.from_model(a) for a in qs]

    @strawberry.field
    def timetable(
        self,
        semester_id: Optional[strawberry.ID] = None,
        class_group: Optional[str] = None,
        teacher_id: Optional[strawberry.ID] = None,
        day_of_week: Optional[str] = None,
    ) -> List[TimetableType]:
        """Get timetable slots. Filter by semester, class group, teacher, or day."""
        qs = Timetable.objects.select_related('subject', 'teacher', 'teacher__user', 'semester')
        if semester_id:
            qs = qs.filter(semester_id=semester_id)
        if class_group:
            qs = qs.filter(class_group=class_group)
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        if day_of_week:
            qs = qs.filter(day_of_week=day_of_week)
        return [TimetableType.from_model(slot) for slot in qs.order_by('day_of_week', 'start_time')]

    @strawberry.field
    def result_cards(
        self,
        student_id: Optional[strawberry.ID] = None,
        semester_id: Optional[strawberry.ID] = None,
        subject_id: Optional[strawberry.ID] = None,
        grade_level: Optional[str] = None,
        academic_year: Optional[str] = None,
    ) -> List[ResultCardType]:
        """Get result cards. Filter by student, semester, subject, grade_level, or academic_year."""
        qs = ResultCard.objects.select_related('student', 'subject', 'semester')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if semester_id:
            qs = qs.filter(semester_id=semester_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if grade_level:
            qs = qs.filter(student__grade_level__iexact=grade_level)
        if academic_year:
            qs = qs.filter(semester__academic_year=academic_year)
        return [ResultCardType.from_model(r) for r in qs]


# Forward references for type hints
from academics.schema.academics_schema import DepartmentType, SemesterType
