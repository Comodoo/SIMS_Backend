"""
Management command to seed initial SIMS data:
  - Default department
  - Admin superuser
  - Sample teacher (Staff)
  - Sample student
  - Active semester

Run with:  python manage.py seed_data
Re-running is safe (idempotent — skips already-existing records).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import datetime


class Command(BaseCommand):
    help = 'Seed initial users (admin, teacher, student) and supporting data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing seed users before re-creating them',
        )

    def handle(self, *args, **options):
        from core.models.core_models import User, Staff, Student
        from academics.models.academic_structure_models import Department, Semester

        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing seed users...'))
            User.objects.filter(username__in=['admin', 'teacher01', 'student01']).delete()

        with transaction.atomic():
            dept = self._ensure_department()
            semester = self._ensure_semester()
            self._ensure_admin()
            self._ensure_teacher(dept)
            self._ensure_student(dept)

        self.stdout.write(self.style.SUCCESS('\nSeed data ready. Login credentials:'))
        self.stdout.write('  Admin   : username=admin       password=admin123')
        self.stdout.write('  Teacher : username=teacher01   password=teacher123')
        self.stdout.write('  Student : username=student01   password=student123')

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_department(self):
        from academics.models.academic_structure_models import Department
        dept, created = Department.objects.get_or_create(
            code='GEN',
            defaults={
                'name': 'General Studies',
                'description': 'Default department',
            }
        )
        if created:
            self.stdout.write('  Created department: General Studies')
        else:
            self.stdout.write('  Department exists: General Studies')
        return dept

    def _ensure_semester(self):
        from academics.models.academic_structure_models import Semester
        sem, created = Semester.objects.get_or_create(
            name='Term 1 2024/2025',
            defaults={
                'academic_year': '2024/2025',
                'start_date': datetime.date(2025, 1, 6),
                'end_date': datetime.date(2025, 4, 30),
                'enrollment_open': datetime.date(2024, 12, 1),
                'enrollment_close': datetime.date(2025, 1, 5),
                'status': 'active',
            }
        )
        label = 'Created' if created else 'Exists '
        self.stdout.write(f'  {label} semester: Term 1 2024/2025')
        return sem

    def _ensure_admin(self):
        from core.models.core_models import User
        if User.objects.filter(username='admin').exists():
            self.stdout.write('  Admin user exists — skipping')
            return
        User.objects.create_superuser(
            username='admin',
            email='admin@sims.edu',
            password='admin123',
            first_name='System',
            last_name='Admin',
            role='admin',
        )
        self.stdout.write('  Created admin user: admin')

    def _ensure_teacher(self, dept):
        from core.models.core_models import User, Staff
        if User.objects.filter(username='teacher01').exists():
            self.stdout.write('  Teacher user exists — skipping')
            return
        user = User.objects.create_user(
            username='teacher01',
            email='teacher01@sims.edu',
            password='teacher123',
            first_name='Jane',
            last_name='Doe',
            role='staff',
        )
        Staff.objects.create(
            user=user,
            department=dept,
            staff_number='STF-001',
            position='Teacher',
            hire_date=datetime.date(2023, 1, 15),
            shift_start_time=datetime.time(7, 30),
            shift_end_time=datetime.time(16, 30),
            is_active=True,
        )
        self.stdout.write('  Created teacher: teacher01')

    def _ensure_student(self, dept):
        from core.models.core_models import User, Student
        if User.objects.filter(username='student01').exists():
            self.stdout.write('  Student user exists — skipping')
            return
        user = User.objects.create_user(
            username='student01',
            email='student01@sims.edu',
            password='student123',
            first_name='John',
            last_name='Smith',
            role='student',
        )
        Student.objects.create(
            user=user,
            department=dept,
            student_number='STD-001',
            first_name='John',
            last_name='Smith',
            grade_level='Form 1',
            academic_year='2024/2025',
            status='active',
        )
        self.stdout.write('  Created student: student01')
