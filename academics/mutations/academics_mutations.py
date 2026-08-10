"""
Academics GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional
from academics.models.academics_models import Course, Enrollment, Assignment, Submission, SubjectTeacher, Timetable
from academics.models.grading_models import ResultCard
from academics.schema.academics_schema import (
    CourseType, EnrollmentType, AssignmentType, SubmissionType,
    CourseInput, AssignmentInput, SubmissionInput, GradeSubmissionInput, EnrollmentInput,
    AssignTeacherInput, TimetableInput, ResultCardInput,
    SubjectTeacherType, TimetableType, ResultCardType,
    SubjectTeacherMutationResponse, TimetableMutationResponse, ResultCardMutationResponse,
    BulkResultCardInput, BulkResultCardMutationResponse, BulkResultRowError,
)


@strawberry.type
class AcademicsMutationResponse:
    """Response type for academics mutations"""
    success: bool
    message: str


@strawberry.type
class CourseMutationResponse(AcademicsMutationResponse):
    """Response type for course mutations"""
    course: Optional[CourseType] = None


@strawberry.type
class AssignmentMutationResponse(AcademicsMutationResponse):
    """Response type for assignment mutations"""
    assignment: Optional[AssignmentType] = None


@strawberry.type
class SubmissionMutationResponse(AcademicsMutationResponse):
    """Response type for submission mutations"""
    submission: Optional[SubmissionType] = None


def _error_response(message: str) -> AcademicsMutationResponse:
    """Helper for error responses"""
    return AcademicsMutationResponse(success=False, message=message)


def _check_timetable_conflicts(semester_id, class_group, teacher_id, day_of_week, start_time, end_time, exclude_slot_id=None):
    """Return (conflict: bool, message: str). Checks class-group and teacher double-booking."""
    qs = Timetable.objects.filter(semester_id=semester_id, day_of_week=day_of_week)
    if exclude_slot_id:
        qs = qs.exclude(timetable_id=exclude_slot_id)

    overlapping = qs.filter(start_time__lt=end_time, end_time__gt=start_time)

    group_clash = overlapping.filter(class_group=class_group).first()
    if group_clash:
        return True, (
            f"Class group '{class_group}' already has '{group_clash.subject.name}' "
            f"on {day_of_week.capitalize()} from {group_clash.start_time.strftime('%H:%M')} "
            f"to {group_clash.end_time.strftime('%H:%M')}."
        )

    teacher_clash = overlapping.filter(teacher_id=teacher_id).first()
    if teacher_clash:
        t = teacher_clash.teacher.user
        return True, (
            f"Teacher {t.first_name} {t.last_name} is already teaching '{teacher_clash.subject.name}' "
            f"to {teacher_clash.class_group} on {day_of_week.capitalize()} "
            f"from {teacher_clash.start_time.strftime('%H:%M')} to {teacher_clash.end_time.strftime('%H:%M')}."
        )

    return False, ""


@strawberry.type
class AcademicsMutation:
    """GraphQL mutations for Academics module"""
    
    @strawberry.mutation
    def create_course(self, input: CourseInput) -> CourseMutationResponse:
        """Create a new course"""
        try:
            from academics.models.academic_structure_models import Department, Semester
            from core.models.core_models import Staff
            
            # Resolve ForeignKey instances
            department = None
            if input.department:
                department = Department.objects.filter(name=input.department).first()
                if not department:
                    department = Department.objects.filter(code=input.department).first()
            
            semester = None
            if input.semester:
                semester = Semester.objects.filter(name=input.semester).first()
                if not semester and input.academic_year:
                    import datetime as dt
                    semester = Semester.objects.create(
                        name=input.semester,
                        academic_year=input.academic_year,
                        start_date=dt.date.today(),
                        end_date=dt.date.today(),
                        enrollment_open=dt.date.today(),
                        enrollment_close=dt.date.today(),
                        status='active',
                    )
            elif input.academic_year:
                semester = Semester.objects.filter(academic_year=input.academic_year, status='active').first()
            
            staff = None
            if input.instructor_id:
                staff = Staff.objects.filter(staff_id=input.instructor_id).first()
            
            course = Course.objects.create(
                course_code=input.course_code,
                name=input.name,
                description=input.description,
                credits=input.credits or 3,
                status=input.status or 'active',
                department=department,
                staff=staff,
                semester=semester,
                max_students=input.max_students or 50,
                class_group=input.class_group or None,
            )
            
            return CourseMutationResponse(
                success=True, 
                message="Course created successfully", 
                course=CourseType.from_model(course)
            )
        except Exception as e:
            return CourseMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def update_course(self, course_id: strawberry.ID, input: CourseInput) -> CourseMutationResponse:
        """Update an existing course"""
        try:
            from academics.models.academic_structure_models import Department, Semester
            from core.models.core_models import Staff
            
            course = Course.objects.get(course_id=course_id)
            
            # Resolve ForeignKey instances
            if input.department:
                department = Department.objects.filter(name=input.department).first()
                if not department:
                    department = Department.objects.filter(code=input.department).first()
                if department:
                    course.department = department
            
            if input.semester:
                semester = Semester.objects.filter(name=input.semester).first()
                if not semester and input.academic_year:
                    import datetime as dt
                    semester = Semester.objects.create(
                        name=input.semester,
                        academic_year=input.academic_year,
                        start_date=dt.date.today(),
                        end_date=dt.date.today(),
                        enrollment_open=dt.date.today(),
                        enrollment_close=dt.date.today(),
                        status='active',
                    )
                if semester:
                    course.semester = semester
            
            if input.instructor_id:
                staff = Staff.objects.filter(staff_id=input.instructor_id).first()
                if staff:
                    course.staff = staff
            
            course.course_code = input.course_code
            course.name = input.name
            course.description = input.description
            course.credits = input.credits or 3
            course.status = input.status or 'active'
            course.max_students = input.max_students or 50
            course.class_group = input.class_group or None
            course.save()
            
            return CourseMutationResponse(
                success=True, 
                message="Course updated successfully", 
                course=CourseType.from_model(course)
            )
        except Course.DoesNotExist:
            return CourseMutationResponse(success=False, message="Course not found")
        except Exception as e:
            return CourseMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def delete_course(self, course_id: strawberry.ID) -> AcademicsMutationResponse:
        """Delete a course"""
        try:
            course = Course.objects.get(course_id=course_id)
            course.delete()
            return AcademicsMutationResponse(success=True, message="Course deleted successfully")
        except Course.DoesNotExist:
            return AcademicsMutationResponse(success=False, message="Course not found")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def approve_course(self, course_id: strawberry.ID) -> CourseMutationResponse:
        """Approve/publish a course"""
        try:
            course = Course.objects.get(course_id=course_id)
            course.status = 'active'
            course.save()
            
            return CourseMutationResponse(
                success=True, 
                message="Course approved successfully", 
                course=CourseType.from_model(course)
            )
        except Course.DoesNotExist:
            return CourseMutationResponse(success=False, message="Course not found")
        except Exception as e:
            return CourseMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def reject_course(self, course_id: strawberry.ID, reason: str) -> AcademicsMutationResponse:
        """Reject a course"""
        try:
            course = Course.objects.get(course_id=course_id)
            course.status = 'inactive'
            course.save()
            
            return AcademicsMutationResponse(success=True, message=f"Course rejected: {reason}")
        except Course.DoesNotExist:
            return AcademicsMutationResponse(success=False, message="Course not found")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def suspend_course(self, course_id: strawberry.ID) -> CourseMutationResponse:
        """Suspend a course"""
        try:
            course = Course.objects.get(course_id=course_id)
            course.status = 'inactive'
            course.save()
            
            return CourseMutationResponse(
                success=True, 
                message="Course suspended successfully", 
                course=CourseType.from_model(course)
            )
        except Course.DoesNotExist:
            return CourseMutationResponse(success=False, message="Course not found")
        except Exception as e:
            return CourseMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def create_assignment(self, input: AssignmentInput) -> AssignmentMutationResponse:
        """Create a new assignment"""
        try:
            assignment = Assignment.objects.create(
                course_id=input.course_id,
                title=input.title,
                description=input.description,
                assignment_type=input.assignment_type or 'homework',
                due_date=input.due_date,
                total_marks=input.total_marks or 100.00,
                attachment_url=input.attachment_url,
                attachment_type=input.attachment_type,
                is_published=input.is_published or False,
                allow_late_submission=input.allow_late_submission or False,
                late_penalty_percent=input.late_penalty_percent or 0.00
            )
            
            return AssignmentMutationResponse(
                success=True, 
                message="Assignment created successfully", 
                assignment=AssignmentType.from_model(assignment)
            )
        except Exception as e:
            return AssignmentMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def update_assignment(self, assignment_id: strawberry.ID, input: AssignmentInput) -> AssignmentMutationResponse:
        """Update an existing assignment"""
        try:
            assignment = Assignment.objects.get(assign_id=assignment_id)
            assignment.course_id = input.course_id
            assignment.title = input.title
            assignment.description = input.description
            assignment.assignment_type = input.assignment_type or 'homework'
            assignment.due_date = input.due_date
            assignment.total_marks = input.total_marks or 100.00
            assignment.attachment_url = input.attachment_url
            assignment.attachment_type = input.attachment_type
            assignment.is_published = input.is_published or False
            assignment.allow_late_submission = input.allow_late_submission or False
            assignment.late_penalty_percent = input.late_penalty_percent or 0.00
            assignment.save()
            
            return AssignmentMutationResponse(
                success=True, 
                message="Assignment updated successfully", 
                assignment=AssignmentType.from_model(assignment)
            )
        except Assignment.DoesNotExist:
            return AssignmentMutationResponse(success=False, message="Assignment not found")
        except Exception as e:
            return AssignmentMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def delete_assignment(self, assignment_id: strawberry.ID) -> AcademicsMutationResponse:
        """Delete an assignment"""
        try:
            assignment = Assignment.objects.get(assign_id=assignment_id)
            assignment.delete()
            return AcademicsMutationResponse(success=True, message="Assignment deleted successfully")
        except Assignment.DoesNotExist:
            return AcademicsMutationResponse(success=False, message="Assignment not found")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def submit_assignment(self, input: SubmissionInput) -> SubmissionMutationResponse:
        """Submit an assignment"""
        try:
            submission = Submission.objects.create(
                student_id=input.student_id,
                assignment_id=input.assignment_id,
                content_text=input.content_text,
                file_url=input.file_url,
                file_type=input.file_type
            )
            
            return SubmissionMutationResponse(
                success=True, 
                message="Assignment submitted successfully", 
                submission=SubmissionType.from_model(submission)
            )
        except Exception as e:
            return SubmissionMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def grade_submission(self, input: GradeSubmissionInput) -> SubmissionMutationResponse:
        """Grade a submission"""
        try:
            from django.utils import timezone as tz
            submission = Submission.objects.get(sub_id=input.submission_id)
            submission.grade = input.grade
            submission.feedback = input.feedback
            submission.status = 'graded'
            submission.graded_at = tz.now()
            submission.save()
            
            return SubmissionMutationResponse(
                success=True, 
                message="Submission graded successfully", 
                submission=SubmissionType.from_model(submission)
            )
        except Submission.DoesNotExist:
            return SubmissionMutationResponse(success=False, message="Submission not found")
        except Exception as e:
            return SubmissionMutationResponse(success=False, message=f"Error: {str(e)}")
    
    @strawberry.mutation
    def enroll_student(self, input: EnrollmentInput) -> AcademicsMutationResponse:
        """Enroll a student in a course"""
        try:
            from academics.models.academic_structure_models import Semester
            semester = Semester.objects.filter(name=input.semester, academic_year=input.academic_year).first()
            enrollment = Enrollment.objects.create(
                student_id=input.student_id,
                course_id=input.course_id,
                semester=semester,
            )
            return AcademicsMutationResponse(success=True, message="Student enrolled successfully")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")

    # --- SubjectTeacher mutations ---

    @strawberry.mutation
    def assign_teacher_to_subject(self, input: AssignTeacherInput, assigned_by_id: strawberry.ID) -> SubjectTeacherMutationResponse:
        """Admin: assign a teacher to a subject (many-to-many)."""
        try:
            from core.models.core_models import Staff, User
            subject = Course.objects.get(course_id=input.subject_id)
            teacher = Staff.objects.get(staff_id=input.teacher_id)
            admin = User.objects.get(user_id=assigned_by_id)
            assignment, created = SubjectTeacher.objects.get_or_create(
                subject=subject,
                teacher=teacher,
                defaults={'assigned_by': admin, 'is_primary': input.is_primary}
            )
            if not created:
                assignment.is_primary = input.is_primary
                assignment.save()
            return SubjectTeacherMutationResponse(
                success=True,
                message="Teacher assigned" if created else "Assignment updated",
                assignment=SubjectTeacherType.from_model(assignment)
            )
        except Course.DoesNotExist:
            return SubjectTeacherMutationResponse(success=False, message="Subject not found")
        except Exception as e:
            return SubjectTeacherMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def remove_teacher_from_subject(self, subject_id: strawberry.ID, teacher_id: strawberry.ID) -> AcademicsMutationResponse:
        """Admin: remove a teacher from a subject."""
        try:
            deleted, _ = SubjectTeacher.objects.filter(
                subject_id=subject_id, teacher_id=teacher_id
            ).delete()
            if deleted:
                return AcademicsMutationResponse(success=True, message="Teacher removed from subject")
            return AcademicsMutationResponse(success=False, message="Assignment not found")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")

    # --- Timetable mutations ---

    @strawberry.mutation
    def create_timetable_slot(self, input: TimetableInput) -> TimetableMutationResponse:
        """Admin: create a timetable slot."""
        try:
            from core.models.core_models import Staff
            from academics.models.academic_structure_models import Semester
            subject = Course.objects.get(course_id=input.subject_id)
            teacher = Staff.objects.get(staff_id=input.teacher_id)
            semester = Semester.objects.get(semester_id=input.semester_id)

            conflict, msg = _check_timetable_conflicts(
                semester_id=semester.semester_id,
                class_group=input.class_group,
                teacher_id=teacher.staff_id,
                day_of_week=input.day_of_week,
                start_time=input.start_time,
                end_time=input.end_time,
            )
            if conflict:
                return TimetableMutationResponse(success=False, message=msg)

            slot = Timetable.objects.create(
                subject=subject,
                teacher=teacher,
                semester=semester,
                class_group=input.class_group,
                day_of_week=input.day_of_week,
                start_time=input.start_time,
                end_time=input.end_time,
                room=input.room,
            )
            return TimetableMutationResponse(
                success=True, message="Timetable slot created",
                slot=TimetableType.from_model(slot)
            )
        except Exception as e:
            return TimetableMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def update_timetable_slot(self, slot_id: strawberry.ID, input: TimetableInput) -> TimetableMutationResponse:
        """Admin: update a timetable slot."""
        try:
            from core.models.core_models import Staff
            from academics.models.academic_structure_models import Semester
            slot = Timetable.objects.get(timetable_id=slot_id)
            teacher = Staff.objects.get(staff_id=input.teacher_id)
            semester = Semester.objects.get(semester_id=input.semester_id)

            conflict, msg = _check_timetable_conflicts(
                semester_id=semester.semester_id,
                class_group=input.class_group,
                teacher_id=teacher.staff_id,
                day_of_week=input.day_of_week,
                start_time=input.start_time,
                end_time=input.end_time,
                exclude_slot_id=slot_id,
            )
            if conflict:
                return TimetableMutationResponse(success=False, message=msg)

            slot.subject = Course.objects.get(course_id=input.subject_id)
            slot.teacher = teacher
            slot.semester = semester
            slot.class_group = input.class_group
            slot.day_of_week = input.day_of_week
            slot.start_time = input.start_time
            slot.end_time = input.end_time
            slot.room = input.room
            slot.save()
            return TimetableMutationResponse(
                success=True, message="Timetable slot updated",
                slot=TimetableType.from_model(slot)
            )
        except Timetable.DoesNotExist:
            return TimetableMutationResponse(success=False, message="Slot not found")
        except Exception as e:
            return TimetableMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def delete_timetable_slot(self, slot_id: strawberry.ID) -> AcademicsMutationResponse:
        """Admin: delete a timetable slot."""
        try:
            Timetable.objects.get(timetable_id=slot_id).delete()
            return AcademicsMutationResponse(success=True, message="Timetable slot deleted")
        except Timetable.DoesNotExist:
            return AcademicsMutationResponse(success=False, message="Slot not found")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")

    # --- ResultCard mutations ---

    @strawberry.mutation
    def compute_result_card(self, input: ResultCardInput, computed_by_id: strawberry.ID) -> ResultCardMutationResponse:
        """Teacher/Admin: create or update a result card for a student in a subject."""
        try:
            from core.models.core_models import Staff, Student
            from academics.models.academic_structure_models import Semester
            from decimal import Decimal

            student = Student.objects.get(student_id=input.student_id)
            subject = Course.objects.get(course_id=input.subject_id)
            semester = Semester.objects.get(semester_id=input.semester_id)
            teacher = Staff.objects.get(staff_id=computed_by_id)

            result, _ = ResultCard.objects.get_or_create(
                student=student, subject=subject, semester=semester,
                defaults={'computed_by': teacher}
            )
            result.cat1_score = input.cat1_score
            result.cat2_score = input.cat2_score
            result.exam_score = input.exam_score
            result.computed_by = teacher

            # Total = CAT1 + CAT2 + Exam (teacher scales each to its weight, e.g. 20+20+60=100)
            scores = [s for s in [input.cat1_score, input.cat2_score, input.exam_score] if s is not None]
            if scores:
                result.total_score = sum(scores)
            result.grade_letter = result.compute_grade_letter()
            # Remarks default to a grade-based comment unless the teacher typed their own.
            result.remarks = input.remarks or result.default_remark()
            result.save()

            return ResultCardMutationResponse(
                success=True, message="Result card saved",
                result=ResultCardType.from_model(result)
            )
        except Exception as e:
            return ResultCardMutationResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def bulk_compute_result_cards(self, input: BulkResultCardInput, computed_by_id: strawberry.ID) -> BulkResultCardMutationResponse:
        """Teacher/Admin: create or update result cards for many students at once (bulk CSV/Excel import)."""
        from core.models.core_models import Staff, Student
        from academics.models.academic_structure_models import Semester

        try:
            subject = Course.objects.get(course_id=input.subject_id)
            semester = Semester.objects.get(semester_id=input.semester_id)
            teacher = Staff.objects.get(staff_id=computed_by_id)
        except Course.DoesNotExist:
            return BulkResultCardMutationResponse(
                success=False, message="Subject not found", saved_count=0,
                failed_count=len(input.rows), results=[], errors=[]
            )
        except Semester.DoesNotExist:
            return BulkResultCardMutationResponse(
                success=False, message="Semester not found", saved_count=0,
                failed_count=len(input.rows), results=[], errors=[]
            )
        except Staff.DoesNotExist:
            return BulkResultCardMutationResponse(
                success=False, message="Teacher not found", saved_count=0,
                failed_count=len(input.rows), results=[], errors=[]
            )

        import uuid as _uuid
        batch_id = _uuid.uuid4()

        saved_results = []
        row_errors = []

        for row in input.rows:
            try:
                student = Student.objects.get(student_id=row.student_id)

                result, _ = ResultCard.objects.get_or_create(
                    student=student, subject=subject, semester=semester,
                    defaults={'computed_by': teacher}
                )
                result.cat1_score = row.cat1_score
                result.cat2_score = row.cat2_score
                result.exam_score = row.exam_score
                result.computed_by = teacher

                scores = [s for s in [row.cat1_score, row.cat2_score, row.exam_score] if s is not None]
                result.total_score = sum(scores) if scores else None
                result.grade_letter = result.compute_grade_letter()
                # Remarks default to a grade-based comment unless the teacher typed their own
                # in the Remarks column of the uploaded sheet.
                result.remarks = row.remarks or result.default_remark()

                # Bulk-imported results start as drafts — hidden from the student until the
                # teacher reviews the batch and explicitly publishes it.
                result.status = 'draft'
                result.batch_id = batch_id
                result.published_at = None
                result.save()

                saved_results.append(ResultCardType.from_model(result))
            except Student.DoesNotExist:
                row_errors.append(BulkResultRowError(student_id=row.student_id, message="Student not found"))
            except Exception as e:
                row_errors.append(BulkResultRowError(student_id=row.student_id, message=str(e)))

        return BulkResultCardMutationResponse(
            success=len(saved_results) > 0,
            message=f"Saved {len(saved_results)} of {len(input.rows)} result card(s) as draft",
            saved_count=len(saved_results),
            failed_count=len(row_errors),
            results=saved_results,
            errors=row_errors,
            batch_id=strawberry.ID(str(batch_id)) if saved_results else None,
        )

    @strawberry.mutation
    def publish_result_batch(self, batch_id: strawberry.ID, published_by_id: strawberry.ID) -> BulkResultCardMutationResponse:
        """Teacher/Admin: publish every result card in a draft batch, making them visible to students."""
        from django.utils import timezone

        batch_qs = ResultCard.objects.filter(batch_id=batch_id)
        count = batch_qs.count()
        if count == 0:
            return BulkResultCardMutationResponse(
                success=False, message="Batch not found", saved_count=0,
                failed_count=0, results=[], errors=[], batch_id=None
            )

        batch_qs.update(status='published', published_at=timezone.now())
        results = [ResultCardType.from_model(r) for r in ResultCard.objects.filter(batch_id=batch_id)]

        return BulkResultCardMutationResponse(
            success=True,
            message=f"Published {count} result(s) — now visible to students",
            saved_count=count,
            failed_count=0,
            results=results,
            errors=[],
            batch_id=batch_id,
        )
