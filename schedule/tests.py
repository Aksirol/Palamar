import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import User, Teacher, Student
from subjects.models import Group, Subject
from .models import Schedule


class ScheduleModelTest(TestCase):
    def setUp(self):
        # Довідкові дані
        self.group = Group.objects.create(name="КН-21", faculty="ФІТ", year_formed=2023)
        self.subject = Subject.objects.create(name="Python", credits=5, semester=3)

        # Викладач
        self.user_teacher = User.objects.create_user(username='teacher1', role='teacher', password='123')
        self.teacher = Teacher.objects.create(user=self.user_teacher, department="ІТ")

        # Базове заняття (Понеділок, 09:00 - 10:30)
        self.lesson1 = Schedule.objects.create(
            subject=self.subject,
            teacher=self.teacher,
            group=self.group,
            day_of_week=1,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 30),
            room="Ауд. 101",
            lesson_type='lecture'
        )

    def test_invalid_time_order(self):
        """Перевірка: час закінчення не може бути раніше часу початку"""
        lesson = Schedule(
            subject=self.subject, teacher=self.teacher, group=self.group,
            day_of_week=1, start_time=datetime.time(11, 0), end_time=datetime.time(10, 0),
            room="Ауд. 102", lesson_type='practice'
        )
        with self.assertRaises(ValidationError) as context:
            lesson.clean()
        self.assertIn("Час закінчення має бути пізніше часу початку", str(context.exception))

    def test_teacher_overlap(self):
        """Перевірка: викладач не може вести дві пари одночасно"""
        group2 = Group.objects.create(name="КН-22", faculty="ФІТ", year_formed=2023)

        overlapping_lesson = Schedule(
            subject=self.subject,
            teacher=self.teacher,  # Той самий викладач
            group=group2,  # Інша група
            day_of_week=1,  # Той самий день
            start_time=datetime.time(9, 30),  # Накладається на 09:00 - 10:30
            end_time=datetime.time(11, 00),
            room="Ауд. 102",  # Інша аудиторія
            lesson_type='practice'
        )

        with self.assertRaises(ValidationError) as context:
            overlapping_lesson.clean()
        self.assertIn("Цей викладач вже має заняття в цей час", str(context.exception))

    def test_room_overlap(self):
        """Перевірка: дві різні групи не можуть бути в одній аудиторії одночасно"""
        user_teacher2 = User.objects.create_user(username='teacher2', role='teacher', password='123')
        teacher2 = Teacher.objects.create(user=user_teacher2, department="ІТ")
        group2 = Group.objects.create(name="КН-22", faculty="ФІТ", year_formed=2023)

        overlapping_lesson = Schedule(
            subject=self.subject, teacher=teacher2, group=group2,
            day_of_week=1, start_time=datetime.time(9, 0), end_time=datetime.time(10, 30),
            room="Ауд. 101",  # ТА САМА АУДИТОРІЯ
            lesson_type='practice'
        )
        with self.assertRaises(ValidationError) as context:
            overlapping_lesson.clean()
        self.assertIn("Ця аудиторія вже зайнята", str(context.exception))