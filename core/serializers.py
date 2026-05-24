"""
Serializers for Core App - SIMS Backend
"""
from rest_framework import serializers
from .models import User, Student, Staff, Attendance, StudentAttendance, Parent, ParentStudentLink


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'password', 'first_name',
            'last_name', 'role', 'phone'
        ]
        read_only_fields = ['user_id']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""
    full_name = serializers.CharField(source='full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'user', 'user_email', 'student_number', 'first_name',
            'last_name', 'full_name', 'date_of_birth', 'address', 'enrollment_date',
            'graduation_date', 'status', 'grade_level', 'section',
            'academic_records', 'created_at', 'updated_at'
        ]
        read_only_fields = ['student_id', 'created_at', 'updated_at']


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff model."""
    full_name = serializers.CharField(source='full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'staff_id', 'user', 'user_email', 'staff_number', 'position',
            'department', 'hire_date', 'termination_date', 'full_name',
            'shift_start_time', 'shift_end_time', 'late_threshold_minutes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['staff_id', 'created_at', 'updated_at']


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model."""
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    department = serializers.CharField(source='staff.department', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'att_id', 'user', 'staff', 'staff_name', 'department', 'timestamp',
            'status', 'method', 'is_late', 'late_minutes', 'notes', 'verified_by',
            'biometric_match_score', 'device_id', 'location', 'created_at'
        ]
        read_only_fields = ['att_id', 'created_at']


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance records."""
    fingerprint_template = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Attendance
        fields = [
            'user', 'status', 'method', 'notes', 'location',
            'device_id', 'fingerprint_template'
        ]
    
    def create(self, validated_data):
        fingerprint_template = validated_data.pop('fingerprint_template', None)
        user = validated_data['user']
        
        # Verify biometric if provided
        if fingerprint_template and user.biometric_hash:
            from core.models import hashlib
            provided_hash = hashlib.sha256(fingerprint_template.encode()).hexdigest()
            # In production, compare against stored hash
            # This is simplified for demo
        
        # Get staff profile if exists
        staff = getattr(user, 'staff_profile', None)
        if staff:
            validated_data['staff'] = staff
        
        return Attendance.objects.create(**validated_data)


class StudentAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for StudentAttendance model."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)
    
    class Meta:
        model = StudentAttendance
        fields = [
            'student_att_id', 'student', 'student_name', 'course', 'course_name',
            'date', 'status', 'marked_by', 'marked_by_name', 'marked_at',
            'notes', 'parent_notified', 'notification_sent_at'
        ]
        read_only_fields = ['student_att_id', 'marked_at', 'notification_sent_at']


class ParentSerializer(serializers.ModelSerializer):
    """Serializer for Parent model."""
    full_name = serializers.CharField(source='full_name', read_only=True)
    
    class Meta:
        model = Parent
        fields = [
            'parent_id', 'user', 'first_name', 'last_name', 'full_name',
            'phone', 'email', 'relationship', 'address', 'emergency_contact',
            'notification_prefs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['parent_id', 'created_at', 'updated_at']


class ParentStudentLinkSerializer(serializers.ModelSerializer):
    """Serializer for ParentStudentLink model."""
    parent_name = serializers.CharField(source='parent.full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = ParentStudentLink
        fields = [
            'link_id', 'parent', 'parent_name', 'student', 'student_name',
            'is_primary', 'created_at'
        ]
        read_only_fields = ['link_id', 'created_at']


# Nested serializers for detailed views
class StudentDetailSerializer(StudentSerializer):
    """Detailed Student serializer with related data."""
    parents = serializers.SerializerMethodField()
    
    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ['parents']
    
    def get_parents(self, obj):
        links = obj.parent_links.select_related('parent')
        return [
            {
                'parent_id': str(link.parent.parent_id),
                'name': link.parent.full_name,
                'relationship': link.parent.relationship,
                'is_primary': link.is_primary,
                'phone': link.parent.phone
            }
            for link in links
        ]


class StaffDetailSerializer(StaffSerializer):
    """Detailed Staff serializer with user info."""
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta(StaffSerializer.Meta):
        fields = StaffSerializer.Meta.fields + ['user_details']


class AttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary statistics."""
    total_staff = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    on_time_percentage = serializers.FloatField()
    date = serializers.DateField()
