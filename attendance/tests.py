import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from accounts.models import User, Student
from subjects.models import Group, Subject
from .models import Attendance


class AttendanceModelTest(TestCase):
    def setUp(self):
        """Підготовка тестової бази даних"""
        # Створюємо групу та предмет
        self.group = Group.objects.create(name="КН-21", faculty="ФІТ", year_formed=2023)
        self.subject = Subject.objects.create(name="Python", credits=5, semester=3)

        # Створюємо студента
        self.user_student = User.objects.create_user(username='test_student', role='student', password='password')
        self.student = Student.objects.create(
            user=self.user_student,
            group=self.group,
            specialty="Комп'ютерні науки",
            year_of_study=2,
            student_card_no="KB-001"
        )

        # Фіксуємо сьогоднішню дату
        self.today = timezone.now().date()

    def test_create_valid_attendance(self):
        """Тест 1: Успішне створення запису на сьогоднішню дату."""
        attendance = Attendance(
            student=self.student,
            subject=self.subject,
            date=self.today,
            is_present=True
        )
        attendance.full_clean()  # Перевіряє всі валідації (включаючи clean() та unique_together)
        attendance.save()

        self.assertEqual(Attendance.objects.count(), 1)
        self.assertTrue(attendance.is_present)

    def test_future_date_validation(self):
        """Тест 2: Перевірка блокування майбутньої дати."""
        tomorrow = self.today + datetime.timedelta(days=1)

        attendance = Attendance(
            student=self.student,
            subject=self.subject,
            date=tomorrow,
            is_present=False,
            reason="Захворів у майбутньому"  # :)
        )

        # Метод clean() має викинути ValidationError
        with self.assertRaises(ValidationError) as context:
            attendance.clean()

        self.assertIn("Не можна відмічати відвідуваність на майбутню дату", str(context.exception))

    def test_unique_together_constraint(self):
        """Тест 3: Перевірка неможливості дублювання записів (unique_together)."""
        # Створюємо перший запис
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.today,
            is_present=True
        )

        # Спробуємо створити ДРУГИЙ запис для того ж студента, предмета і дати
        duplicate_attendance = Attendance(
            student=self.student,
            subject=self.subject,
            date=self.today,
            is_present=False
        )

        # Django має викинути ValidationError при перевірці моделі
        with self.assertRaises(ValidationError):
            duplicate_attendance.full_clean()

        # Або IntegrityError, якщо ми спробуємо зберегти це в БД в обхід full_clean()
        with self.assertRaises(IntegrityError):
            duplicate_attendance.save()