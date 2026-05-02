import json
from django.test import TestCase
from django.urls import reverse
from accounts.models import User, Student, Teacher
from subjects.models import Group, Subject
from grades.models import Grade


class ReportsModuleTest(TestCase):
    def setUp(self):
        """Підготовка тестової бази даних"""
        # 1. Довідкові дані
        self.group = Group.objects.create(name="КН-21", faculty="ФІТ", year_formed=2023)
        self.subject_math = Subject.objects.create(name="Вища математика", credits=5, semester=1)
        self.subject_prog = Subject.objects.create(name="Програмування", credits=6, semester=1)

        # 2. Створюємо викладача та студента
        self.user_teacher = User.objects.create_user(username='teacher', role='teacher', password='123')
        self.teacher = Teacher.objects.create(user=self.user_teacher, department="ІТ")

        self.user_student = User.objects.create_user(username='student', role='student', password='123')
        self.student = Student.objects.create(
            user=self.user_student, group=self.group, specialty="КН", year_of_study=1, student_card_no="001"
        )

        # 3. Виставляємо тестові оцінки
        # Вища математика: 90 та 80 (Середній бал має вийти 85.0)
        Grade.objects.create(student=self.student, subject=self.subject_math, teacher=self.teacher, value=90,
                             type='current')
        Grade.objects.create(student=self.student, subject=self.subject_math, teacher=self.teacher, value=80,
                             type='module')

        # Програмування: 100 (Середній бал має вийти 100.0)
        Grade.objects.create(student=self.student, subject=self.subject_prog, teacher=self.teacher, value=100,
                             type='exam')

    def test_student_dashboard_chart_data(self):
        """Тест 1: Перевірка правильності розрахунку середнього бала для Chart.js"""
        # Авторизуємося як студент
        self.client.login(username='student', password='123')

        # Робимо запит на сторінку дашборду
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Витягуємо JSON-рядок із контексту шаблону і перетворюємо його на словник Python
        chart_data_json = response.context['chart_data_json']
        chart_data = json.loads(chart_data_json)

        # Перевіряємо, чи потрапили наші предмети у підписи графіка
        self.assertIn("Вища математика", chart_data['labels'])
        self.assertIn("Програмування", chart_data['labels'])

        # Знаходимо, на якій позиції стоять наші предмети, щоб перевірити їхні бали
        math_index = chart_data['labels'].index("Вища математика")
        prog_index = chart_data['labels'].index("Програмування")

        # Найголовніше: перевіряємо, чи Django правильно порахував середній бал
        self.assertEqual(chart_data['data'][math_index], 85.0)
        self.assertEqual(chart_data['data'][prog_index], 100.0)

    def test_pdf_report_generation(self):
        """Тест 2: Перевірка успішної генерації PDF файлу через WeasyPrint"""
        self.client.login(username='student', password='123')

        # Робимо запит на завантаження PDF
        response = self.client.get(reverse('export_pdf'))

        # Перевіряємо, чи успішний запит і чи браузер розпізнає це як PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

        # Перевіряємо, чи правильне ім'я файлу генерується у заголовках
        self.assertIn('filename="transcript_student.pdf"', response['Content-Disposition'])

        # PDF-файли на бінарному рівні завжди починаються з підпису %PDF-
        # Перевіряємо ці магічні байти, щоб переконатися, що це не пустий файл і не HTML-помилка
        self.assertTrue(response.content.startswith(b'%PDF-'))