from django.test import TestCase
from subjects.models import Group
from .models import User, Student, Teacher


class AccountsModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="КН-21", faculty="ФІТ", year_formed=2023)

    def test_create_student_profile(self):
        """Перевірка успішного створення користувача з профілем студента"""
        user = User.objects.create_user(
            username='new_student',
            email='student@test.com',
            password='password123',
            role='student'
        )
        student = Student.objects.create(
            user=user,
            group=self.group,
            specialty="КН",
            year_of_study=1,
            student_card_no="12345"
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.role, 'student')
        self.assertEqual(student.user.username, 'new_student')
        self.assertEqual(str(student), f"Студент: {user.get_full_name()}")

    def test_create_superuser(self):
        """Перевірка створення адміністратора"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)