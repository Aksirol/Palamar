from django.test import TestCase
from django.urls import reverse
from accounts.models import User, Student, Teacher
from .models import Subject


class SubjectAccessTest(TestCase):
    def setUp(self):
        # Створюємо предмет
        self.subject = Subject.objects.create(name="Фізика", credits=4, semester=2)

        # Створюємо студента
        self.student_user = User.objects.create_user(username='student', role='student', password='123')

        # Створюємо викладача
        self.teacher_user = User.objects.create_user(username='teacher', role='teacher', password='123')
        Teacher.objects.create(user=self.teacher_user, department="Фізика")

    def test_student_access_denied(self):
        """Студент отримує помилку 403 (Forbidden) при спробі додати предмет"""
        self.client.login(username='student', password='123')

        # Намагаємось зайти на сторінку додавання предмета
        response = self.client.get(reverse('subject_add'))

        # 403 означає "Доступ заборонено"
        self.assertEqual(response.status_code, 403)

    def test_teacher_access_allowed(self):
        """Викладач отримує успішний доступ 200 (OK) до додавання предмета"""
        self.client.login(username='teacher', password='123')

        response = self.client.get(reverse('subject_add'))

        # 200 означає "Сторінка успішно завантажена"
        self.assertEqual(response.status_code, 200)