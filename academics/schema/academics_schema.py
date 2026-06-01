"""
Academics GraphQL Schema (Strawberry)
Courses/Subjects, Enrollment, Assignments, Submissions,
SubjectTeacher, Timetable, ResultCard
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from academics.models.academics_models import Course, Enrollment, Assignment, Submission, SubjectTeacher, Timetable
from academics.models.grading_models import ResultCard
from core.schema.core_schema import StaffType, StudentType
from academics.models.academic_structure_models import Department, Semester

@strawberry.type
class DepartmentType:
    """GraphQL type for Department"""
    id: strawberry.ID
    name: str
    code: str
    description: Optional[str] = None

    @classmethod
    def from_model(cls, instance: Department):
        return cls(
            id=strawberry.ID(str(instance.dept_id)),
            name=instance.name,
            code=instance.code,
            description=instance.description
        )

@strawberry.type
class SemesterType:
    """GraphQL type for Semester"""
    id: strawberry.ID
    name: str
    academic_year: str = strawberry.field(name="academic_year")
    start_date: date = strawberry.field(name="start_date")
    end_date: date = strawberry.field(name="end_date")
    status: str

    @classmethod
    def from_model(cls, instance: Semester):
        return cls(
            id=strawberry.ID(str(instance.semester_id)),
            name=instance.name,
            academic_year=instance.academic_year,
            start_date=instance.start_date,
            end_date=instance.end_date,
            status=instance.status
        )

@strawberry.type
class CourseType:
    """GraphQL type for Course (updated for 21-table schema)"""
    id: strawberry.ID
    name: str
    course_code: str = strawberry.field(name="course_code")
    description: Optional[str] = None
    department: str = strawberry.field(resolver=lambda self: self.department_name)
    credits: int
    status: str
    max_students: int = strawberry.field(name="max_students")
    semester: str = strawberry.field(resolver=lambda self: self.semester_name)
    academic_year: str = strawberry.field(name="academic_year", resolver=lambda self: self.academic_year_val)
    class_group: Optional[str] = strawberry.field(name="class_group")
    staff: Optional[StaffType] = None
    created_at: datetime = strawberry.field(name="created_at")
    updated_at: datetime = strawberry.field(name="updated_at")

    # Internal fields for resolvers
    department_name: strawberry.Private[str]
    semester_name: strawberry.Private[str]
    academic_year_val: strawberry.Private[str]

    @classmethod
    def from_model(cls, instance: Course):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.course_id)),
            name=instance.name,
            course_code=instance.course_code,
            description=instance.description,
            department_name=instance.department.name if instance.department else "N/A",
            credits=instance.credits,
            status=instance.status,
            max_students=instance.max_students,
            class_group=instance.class_group,
            semester_name=instance.semester.name if instance.semester else "N/A",
            academic_year_val=instance.semester.academic_year if instance.semester else "N/A",
            staff=StaffType.from_model(instance.staff) if instance.staff else None,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class EnrollmentType:
    """GraphQL type for Enrollment (updated for 21-table schema with frontend compatibility)"""
    id: strawberry.ID
    student: StudentType
    course: CourseType
    enrolled_at: datetime = strawberry.field(name="enrolled_at")
    status: str
    semester: str
    academic_year: str = strawberry.field(name="academic_year")
    midterm_grade: Optional[float] = strawberry.field(name="midterm_grade")
    final_grade: Optional[float] = strawberry.field(name="final_grade")
    letter_grade: Optional[str] = strawberry.field(name="letter_grade")
    
    @classmethod
    def from_model(cls, instance: Enrollment):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.enrollment_id)),
            student=StudentType.from_model(instance.student),
            course=CourseType.from_model(instance.course),
            enrolled_at=instance.enrolled_at,
            status=instance.status,
            semester=instance.semester.name if instance.semester else "",
            academic_year=instance.semester.academic_year if instance.semester else "",
            midterm_grade=None,
            final_grade=instance.final_grade,
            letter_grade=instance.grade_letter,
        )


@strawberry.type
class AssignmentType:
    """GraphQL type for Assignment"""
    id: strawberry.ID
    course: CourseType
    title: str
    description: str
    assignmentType: str
    dueDate: datetime
    totalMarks: Decimal
    attachmentUrl: Optional[str] = None
    attachmentType: Optional[str] = None
    isPublished: bool
    allowLateSubmission: bool
    latePenaltyPercent: Decimal
    isOverdue: bool
    submissionCount: int
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_model(cls, instance: Assignment):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.assign_id)),
            course=CourseType.from_model(instance.course),
            title=instance.title,
            description=instance.description,
            assignmentType=instance.assignment_type,
            dueDate=instance.due_date,
            totalMarks=instance.total_marks,
            attachmentUrl=instance.attachment_url,
            attachmentType=instance.attachment_type,
            isPublished=instance.is_published,
            allowLateSubmission=instance.allow_late_submission,
            latePenaltyPercent=instance.late_penalty_percent,
            isOverdue=instance.is_overdue,
            submissionCount=instance.submissions.count(),
            createdAt=instance.created_at,
            updatedAt=instance.updated_at,
        )


@strawberry.type
class SubmissionType:
    """GraphQL type for Submission"""
    id: strawberry.ID
    student: StudentType
    assignment: AssignmentType
    submitted_at: datetime
    status: str
    content_text: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None
    graded_by: Optional[StaffType] = None
    graded_at: Optional[datetime] = None
    plagiarism_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, instance: Submission):
        """Convert model instance to GraphQL type"""
        return cls(
            id=strawberry.ID(str(instance.sub_id)),
            student=StudentType.from_model(instance.student),
            assignment=AssignmentType.from_model(instance.assignment),
            submitted_at=instance.submitted_at,
            status=instance.status,
            content_text=instance.content_text,
            file_url=instance.file_url,
            file_type=instance.file_type,
            grade=instance.grade,
            feedback=instance.feedback,
            graded_by=StaffType.from_model(instance.graded_by) if instance.graded_by else None,
            graded_at=instance.graded_at,
            plagiarism_score=instance.plagiarism_score,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )


@strawberry.type
class SubjectTeacherType:
    """GraphQL type for SubjectTeacher assignment"""
    id: strawberry.ID
    subject_id: strawberry.ID
    subject_name: str
    teacher: StaffType
    is_primary: bool
    assigned_at: datetime

    @classmethod
    def from_model(cls, instance: SubjectTeacher):
        return cls(
            id=strawberry.ID(str(instance.id)),
            subject_id=strawberry.ID(str(instance.subject.course_id)),
            subject_name=instance.subject.name,
            teacher=StaffType.from_model(instance.teacher),
            is_primary=instance.is_primary,
            assigned_at=instance.assigned_at,
        )


@strawberry.type
class TimetableType:
    """GraphQL type for Timetable slot"""
    id: strawberry.ID
    subject: CourseType
    teacher: Optional[StaffType]
    semester_id: strawberry.ID
    semester_name: str
    class_group: str
    day_of_week: str
    start_time: time
    end_time: time
    room: Optional[str]
    created_at: datetime

    @classmethod
    def from_model(cls, instance: Timetable):
        return cls(
            id=strawberry.ID(str(instance.timetable_id)),
            subject=CourseType.from_model(instance.subject),
            teacher=StaffType.from_model(instance.teacher) if instance.teacher else None,
            semester_id=strawberry.ID(str(instance.semester.semester_id)),
            semester_name=instance.semester.name,
            class_group=instance.class_group,
            day_of_week=instance.day_of_week,
            start_time=instance.start_time,
            end_time=instance.end_time,
            room=instance.room,
            created_at=instance.created_at,
        )


@strawberry.type
class ResultCardType:
    """GraphQL type for ResultCard"""
    id: strawberry.ID
    student: StudentType
    subject: CourseType
    semester_id: strawberry.ID
    semester_name: str
    cat1_score: Optional[Decimal]
    cat2_score: Optional[Decimal]
    exam_score: Optional[Decimal]
    total_score: Optional[Decimal]
    grade_letter: Optional[str]
    remarks: Optional[str]
    computed_at: datetime

    @classmethod
    def from_model(cls, instance: ResultCard):
        return cls(
            id=strawberry.ID(str(instance.result_id)),
            student=StudentType.from_model(instance.student),
            subject=CourseType.from_model(instance.subject),
            semester_id=strawberry.ID(str(instance.semester.semester_id)),
            semester_name=instance.semester.name,
            cat1_score=instance.cat1_score,
            cat2_score=instance.cat2_score,
            exam_score=instance.exam_score,
            total_score=instance.total_score,
            grade_letter=instance.grade_letter,
            remarks=instance.remarks,
            computed_at=instance.computed_at,
        )


# Input Types for Mutations
@strawberry.input
class CourseInput:
    """Input for creating/updating Course"""
    course_code: str
    name: str
    description: Optional[str] = None
    credits: int = 3
    status: str = "active"
    level: str = "beginner"
    department: Optional[str] = None
    instructor_id: Optional[strawberry.ID] = None
    schedule: Optional[str] = None
    prerequisites: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    max_students: int = 50
    class_group: Optional[str] = None


@strawberry.input
class AssignmentInput:
    """Input for creating/updating Assignment"""
    course_id: strawberry.ID
    title: str
    description: str
    assignment_type: str = "homework"
    due_date: datetime
    total_marks: Decimal = Decimal("100.00")
    attachment_url: Optional[str] = None
    attachment_type: Optional[str] = None
    is_published: bool = False
    allow_late_submission: bool = False
    late_penalty_percent: Decimal = Decimal("0.00")


@strawberry.input
class SubmissionInput:
    """Input for creating/updating Submission"""
    student_id: strawberry.ID
    assignment_id: strawberry.ID
    content_text: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None


@strawberry.input
class GradeSubmissionInput:
    """Input for grading a submission"""
    submission_id: strawberry.ID
    grade: str
    feedback: Optional[str] = None


@strawberry.input
class EnrollmentInput:
    """Input for creating/updating Enrollment"""
    student_id: strawberry.ID
    course_id: strawberry.ID
    semester: str
    academic_year: str


# Response Types for Mutations
@strawberry.type
class CourseMutationResponse:
    """Response for Course mutations"""
    success: bool
    message: str
    course: Optional[CourseType] = None


@strawberry.type
class AssignmentMutationResponse:
    """Response for Assignment mutations"""
    success: bool
    message: str
    assignment: Optional[AssignmentType] = None


@strawberry.type
class SubmissionMutationResponse:
    """Response for Submission mutations"""
    success: bool
    message: str
    submission: Optional[SubmissionType] = None


@strawberry.type
class EnrollmentMutationResponse:
    """Response for Enrollment mutations"""
    success: bool
    message: str
    enrollment: Optional[EnrollmentType] = None


# --- New inputs for SubjectTeacher, Timetable, ResultCard ---

@strawberry.input
class AssignTeacherInput:
    subject_id: strawberry.ID
    teacher_id: strawberry.ID
    is_primary: bool = False


@strawberry.input
class TimetableInput:
    subject_id: strawberry.ID
    teacher_id: strawberry.ID
    semester_id: strawberry.ID
    class_group: str
    day_of_week: str
    start_time: time
    end_time: time
    room: Optional[str] = None


@strawberry.input
class ResultCardInput:
    student_id: strawberry.ID
    subject_id: strawberry.ID
    semester_id: strawberry.ID
    cat1_score: Optional[Decimal] = None
    cat2_score: Optional[Decimal] = None
    exam_score: Optional[Decimal] = None
    remarks: Optional[str] = None


@strawberry.type
class SubjectTeacherMutationResponse:
    success: bool
    message: str
    assignment: Optional[SubjectTeacherType] = None


@strawberry.type
class TimetableMutationResponse:
    success: bool
    message: str
    slot: Optional[TimetableType] = None


@strawberry.type
class ResultCardMutationResponse:
    success: bool
    message: str
    result: Optional[ResultCardType] = None
