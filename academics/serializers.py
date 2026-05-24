"""
Serializers for Academics App
"""
from rest_framework import serializers
from .models import Course, Enrollment, Assignment, Submission


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    current_enrollment = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'course_id', 'course_code', 'name', 'description', 'credits',
            'status', 'level', 'department', 'instructor', 'instructor_name',
            'schedule', 'prerequisites', 'semester', 'academic_year',
            'max_students', 'current_enrollment', 'available_seats',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['course_id', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for course lists."""
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'course_id', 'course_code', 'name', 'credits',
            'status', 'level', 'instructor_name'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_number = serializers.CharField(source='student.student_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'enrollment_id', 'student', 'student_name', 'student_number',
            'course', 'course_name', 'course_code', 'enrollment_date',
            'status', 'semester', 'academic_year', 'midterm_grade',
            'final_grade', 'letter_grade'
        ]
        read_only_fields = ['enrollment_id', 'enrollment_date']


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model."""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'assign_id', 'course', 'course_name', 'course_code', 'title',
            'description', 'assignment_type', 'due_date', 'total_marks',
            'attachment_url', 'attachment_type', 'is_published',
            'allow_late_submission', 'late_penalty_percent', 'is_overdue',
            'submission_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['assign_id', 'created_at', 'updated_at']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'sub_id', 'student', 'student_name', 'assignment', 'assignment_title',
            'submitted_at', 'status', 'content_text', 'file_url', 'file_type',
            'grade', 'feedback', 'graded_by', 'graded_by_name', 'graded_at',
            'plagiarism_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sub_id', 'submitted_at', 'created_at', 'updated_at']


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating submissions."""
    
    class Meta:
        model = Submission
        fields = ['assignment', 'content_text', 'file_url', 'file_type']
    
    def validate(self, data):
        assignment = data.get('assignment')
        user = self.context['request'].user
        
        # Get student from user
        try:
            student = user.student_profile
        except AttributeError:
            raise serializers.ValidationError("User is not a student")
        
        # Check if already submitted
        if Submission.objects.filter(student=student, assignment=assignment).exists():
            raise serializers.ValidationError("Already submitted for this assignment")
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        student = user.student_profile
        
        return Submission.objects.create(student=student, **validated_data)


class GradeSubmissionSerializer(serializers.Serializer):
    """Serializer for grading submissions."""
    grade = serializers.CharField(required=True)
    feedback = serializers.CharField(required=False, allow_blank=True)
