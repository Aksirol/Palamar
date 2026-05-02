from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import User, Student, Teacher
from subjects.models import Group, Subject
from .models import Grade

class GradeModelTest(TestCase):
    def setUp(self):
        """
        Цей метод запускається ПЕРЕД кожним тестом.
        Тут ми створюємо "віртуальну" базу даних з тестовими даними.
        Після виконання тестів ці дані автоматично видаляться.
        """
        # 1. Створюємо довідкові дані
        self.group = Group.objects.create(name="КН-21", faculty="ФІТ", year_formed=2023)
        self.subject = Subject.objects.create(name="Python", credits=5, semester=3)

        # 2. Створюємо студента
        self.user_student = User.objects.create_user(username='test_student', role='student', password='testpassword')
        self.student = Student.objects.create(
            user=self.user_student,
            group=self.group,
            specialty="Комп'ютерні науки",
            year_of_study=2,
            student_card_no="KB-12345"
        )

        # 3. Створюємо викладача
        self.user_teacher = User.objects.create_user(username='test_teacher', role='teacher', password='testpassword')
        self.teacher = Teacher.objects.create(user=self.user_teacher, department="Програмування")

    def test_create_valid_grade(self):
        """Тест 1: Перевіряємо, чи успішно створюється звичайна поточна оцінка."""
        grade = Grade(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            value=95,
            type='current'
        )
        grade.clean()  # Викликаємо нашу валідацію вручну
        grade.save()   # Зберігаємо в базу

        self.assertEqual(Grade.objects.count(), 1) # Перевіряємо, що запис з'явився
        self.assertEqual(grade.value, 95)          # Перевіряємо, що бал зберігся правильно

    def test_only_one_exam_per_subject(self):
        """Тест 2: Перевіряємо, чи система блокує спробу поставити ДВА іспити."""
        # Крок 1: Ставимо перший іспит (має пройти успішно)
        Grade.objects.create(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            value=90,
            type='exam'
        )

        # Крок 2: Створюємо другий іспит з того ж предмета
        duplicate_exam = Grade(
            student=self.student,
            subject=self.subject,
            teacher=self.teacher,
            value=85,
            type='exam'
        )

        # Крок 3: Перевіряємо, чи викине система помилку ValidationError
        with self.assertRaises(ValidationError):
            duplicate_exam.clean() # Цей рядок МАЄ викликати помилку валідації