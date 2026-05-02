import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, Student, Teacher
from subjects.models import Group, Subject
from .models import Assignment, Submission
from .forms import SubmissionForm


class AssignmentAndSubmissionTest(TestCase):
    def setUp(self):
        """Підготовка бази даних перед кожним тестом"""
        # 1. Довідкові дані
        self.group = Group.objects.create(name="КН-21", faculty="ФІТ", year_formed=2023)
        self.subject = Subject.objects.create(name="Бази даних", credits=4, semester=3)

        # 2. Користувачі
        self.user_teacher = User.objects.create_user(username='teacher', role='teacher', password='123')
        self.teacher = Teacher.objects.create(user=self.user_teacher, department="ІТ")

        self.user_student = User.objects.create_user(username='student', role='student', password='123')
        self.student = Student.objects.create(
            user=self.user_student, group=self.group, specialty="КН", year_of_study=2, student_card_no="111"
        )

        # 3. Базове завдання з дедлайном ЗАВТРА
        self.future_deadline = timezone.now() + datetime.timedelta(days=1)
        self.assignment = Assignment.objects.create(
            subject=self.subject,
            teacher=self.teacher,
            title="Лабораторна №1",
            description="Зробити ER-діаграму",
            deadline=self.future_deadline,
            max_score=100
        )

    def test_valid_submission(self):
        """Тест 1: Успішна здача роботи (текст без файлу) до дедлайну"""
        submission = Submission(
            assignment=self.assignment,
            student=self.student,
            text_answer="Ось моє посилання на GitHub",
            status='submitted'
        )
        submission.full_clean()  # Має пройти без помилок
        submission.save()
        self.assertEqual(Submission.objects.count(), 1)

    def test_empty_submission_fails(self):
        """Тест 2: Спроба здати порожню роботу (ні файлу, ні тексту)"""
        submission = Submission(
            assignment=self.assignment,
            student=self.student,
            status='submitted'
        )
        with self.assertRaises(ValidationError) as context:
            submission.clean()
        self.assertIn("Необхідно прикріпити файл або написати текстову відповідь", str(context.exception))

    def test_past_deadline_submission_fails(self):
        """Тест 3: Спроба здати роботу ПІСЛЯ дедлайну"""
        # Створюємо прострочене завдання
        past_deadline = timezone.now() - datetime.timedelta(hours=1)
        late_assignment = Assignment.objects.create(
            subject=self.subject, teacher=self.teacher, title="Старе завдання",
            description="Тест", deadline=past_deadline
        )

        submission = Submission(
            assignment=late_assignment,
            student=self.student,
            text_answer="Вибачте за запізнення",
            status='submitted'
        )
        with self.assertRaises(ValidationError) as context:
            submission.clean()
        self.assertIn("Дедлайн минув", str(context.exception))

    def test_status_reversion_fails(self):
        """Тест 4: Спроба змінити статус з 'Перевірено' назад на 'Здано'"""
        # Спершу створюємо і зберігаємо перевірену роботу
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            text_answer="Відповідь", status='checked', score=95
        )

        # Тепер намагаємось змінити статус назад
        submission.status = 'submitted'
        with self.assertRaises(ValidationError) as context:
            submission.clean()
        self.assertIn("Неможливо скасувати перевірку", str(context.exception))

    def test_form_file_extension_validation(self):
        """Тест 5: Перевірка валідації формату файлу у формі (Форма, а не модель)"""
        # Імітуємо завантаження файлу .jpg
        bad_file = SimpleUploadedFile("virus.exe", b"fake file content", content_type="application/x-msdownload")

        # Передаємо файл у форму
        form = SubmissionForm(data={'text_answer': ''}, files={'file': bad_file})

        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)
        self.assertIn("Дозволені лише файли у форматах", form.errors['file'][0])

    def test_form_file_size_validation(self):
        """Тест 6: Перевірка блокування завеликого файлу (>5 МБ)"""
        # Створюємо файл розміром трохи більше 5 МБ (5 * 1024 * 1024 + 1 байт)
        huge_content = b"0" * (5 * 1024 * 1024 + 1)
        huge_file = SimpleUploadedFile("big_archive.zip", huge_content, content_type="application/zip")

        form = SubmissionForm(data={}, files={'file': huge_file})

        self.assertFalse(form.is_valid())
        self.assertIn("Файл занадто великий", form.errors['file'][0])