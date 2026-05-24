"""
Academics GraphQL Mutations (Strawberry)
"""

import strawberry
from typing import Optional
from academics.models.academics_models import Course, Enrollment, Assignment, Submission
from academics.schema.academics_schema import CourseType, EnrollmentType, AssignmentType, SubmissionType, CourseInput, AssignmentInput, SubmissionInput, GradeSubmissionInput, EnrollmentInput


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
                max_students=input.max_students or 50
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
    def toggle_featured(self, course_id: strawberry.ID, is_featured: bool) -> CourseMutationResponse:
        """Toggle course featured status"""
        try:
            course = Course.objects.get(course_id=course_id)
            # Note: Course model doesn't have is_featured field - this would need to be added to the model
            # For now, we'll update the schedule or add a custom field
            if not course.schedule:
                course.schedule = {}
            if isinstance(course.schedule, str):
                import json
                course.schedule = json.loads(course.schedule)
            course.schedule['is_featured'] = is_featured
            course.save()
            
            return CourseMutationResponse(
                success=True, 
                message=f"Course {'featured' if is_featured else 'unfeatured'} successfully", 
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
            submission = Submission.objects.get(sub_id=input.submission_id)
            submission.grade = input.grade
            submission.feedback = input.feedback
            submission.graded_by_id = input.graded_by_id
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
            enrollment = Enrollment.objects.create(
                student_id=input.student_id,
                course_id=input.course_id,
                semester=input.semester,
                academic_year=input.academic_year
            )
            
            return AcademicsMutationResponse(success=True, message="Student enrolled successfully")
        except Exception as e:
            return AcademicsMutationResponse(success=False, message=f"Error: {str(e)}")
