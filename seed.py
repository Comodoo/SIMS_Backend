import os
import django
import uuid
from datetime import date, datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sims_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models.core_models import Student, Staff, Attendance
from academics.models.academics_models import Course
from academics.models.academic_structure_models import Department, Semester

User = get_user_model()

def seed_data():
    print("Starting data seeding...")
    
    # 1. Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin', first_name='System', last_name='Admin')
        print("Superuser 'admin' created.")
    
    # 2. Create Departments
    cs_dept, _ = Department.objects.get_or_create(
        name='Computer Science',
        defaults={'code': 'CS', 'description': 'Department of Computer Science'}
    )
    eng_dept, _ = Department.objects.get_or_create(
        name='Engineering',
        defaults={'code': 'ENG', 'description': 'Department of Engineering'}
    )
    print("Departments created.")
    
    # 3. Create Semester
    semester, _ = Semester.objects.get_or_create(
        name='Fall 2024',
        defaults={
            'academic_year': '2024-2025',
            'start_date': date(2024, 9, 1),
            'end_date': date(2024, 12, 20),
            'enrollment_open': date(2024, 8, 1),
            'enrollment_close': date(2024, 9, 15),
            'status': 'active'
        }
    )
    print("Semester created.")
    
    # 4. Create Staff/Instructor
    if not User.objects.filter(username='instructor1').exists():
        instructor_user = User.objects.create_user(
            username='instructor1',
            email='john@example.com',
            password='temp123',
            role='staff',
            first_name='John',
            last_name='Smith'
        )
        Staff.objects.create(
            user=instructor_user,
            staff_number='STA001',
            position='Senior Lecturer',
            department=cs_dept,
            hire_date=date(2023, 1, 1),
            employment_type='full-time'
        )
        print("Staff 'instructor1' created.")
    else:
        instructor_user = User.objects.get(username='instructor1')
    
    # 5. Create more Students
    students_data = [
        {'username': 'student1', 'email': 'sarah@example.com', 'first': 'Sarah', 'last': 'Johnson', 'num': 'STU001', 'level': 'Sophomore'},
        {'username': 'student2', 'email': 'mike@example.com', 'first': 'Mike', 'last': 'Brown', 'num': 'STU002', 'level': 'Freshman'},
        {'username': 'student3', 'email': 'emily@example.com', 'first': 'Emily', 'last': 'Davis', 'num': 'STU003', 'level': 'Senior'},
    ]
    
    students = []
    for s in students_data:
        if not User.objects.filter(username=s['username']).exists():
            u = User.objects.create_user(
                username=s['username'], email=s['email'], password='temp123',
                role='student', first_name=s['first'], last_name=s['last']
            )
            student = Student.objects.create(
                user=u, student_number=s['num'], first_name=s['first'], last_name=s['last'],
                department=cs_dept, enrollment_date=date(2023, 6, 1), status='active',
                grade_level=s['level'], academic_year='2024'
            )
            students.append(student)
            print(f"Student '{s['username']}' created.")
        else:
            students.append(Student.objects.get(user__username=s['username']))

    # 6. Create Courses
    course1, _ = Course.objects.get_or_create(
        course_code='CS101',
        defaults={
            'name': 'Introduction to Programming',
            'description': 'Basic programming concepts using Python.',
            'department': cs_dept,
            'staff': Staff.objects.get(user=instructor_user),
            'semester': semester,
            'credits': 4,
            'max_students': 50,
            'status': 'active'
        }
    )
    course2, _ = Course.objects.get_or_create(
        course_code='CS201',
        defaults={
            'name': 'Web Development',
            'description': 'Full-stack web development with React and Django.',
            'department': cs_dept,
            'staff': Staff.objects.get(user=instructor_user),
            'semester': semester,
            'credits': 3,
            'max_students': 40,
            'status': 'active'
        }
    )
    print("Courses created.")

    # 7. Create Enrollments
    from academics.models.academics_models import Enrollment
    for student in students:
        Enrollment.objects.get_or_create(
            student=student,
            course=course1,
            defaults={'semester': semester, 'status': 'active'}
        )
        Enrollment.objects.get_or_create(
            student=student,
            course=course2,
            defaults={'semester': semester, 'status': 'active'}
        )
    print("Enrollments created.")

    # 8. Create Attendance Records
    for student in students:
        from core.models.core_models import StudentAttendance
        for i in range(5):
            StudentAttendance.objects.get_or_create(
                student=student,
                course=course1,
                date=date(2024, 4, 25 + i),
                defaults={'status': 'present' if i % 4 != 0 else 'absent', 'semester': semester}
            )
    print("Attendance records created.")

    # 9. Create Assignments
    from academics.models.academics_models import Assignment
    Assignment.objects.get_or_create(
        course=course1,
        title='Python Basics Quiz',
        defaults={
            'description': 'A simple quiz on Python variables and loops.',
            'assignment_type': 'quiz',
            'due_date': datetime(2024, 5, 10),
            'total_marks': 20,
            'is_published': True
        }
    )
    Assignment.objects.get_or_create(
        course=course2,
        title='React Component Lab',
        defaults={
            'description': 'Create a functional component with hooks.',
            'assignment_type': 'lab',
            'due_date': datetime(2024, 5, 15),
            'total_marks': 50,
            'is_published': True
        }
    )
    print("Assignments created.")
    
    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
