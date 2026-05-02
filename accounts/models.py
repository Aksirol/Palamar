from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Адміністратор'),
        ('teacher', 'Викладач'),
        ('student', 'Студент'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name='Роль')
    # Додаємо фото з дефолтним зображенням (завантаж якесь базове фото в media/avatars/default.png)
    photo = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name='Фото профілю', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', primary_key=True)
    department = models.CharField(max_length=100, verbose_name='Кафедра/Відділення')
    academic_degree = models.CharField(max_length=100, blank=True, null=True, verbose_name='Вчений ступінь')

    def __str__(self):
        return f"Викладач: {self.user.get_full_name()}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', primary_key=True)
    group = models.ForeignKey('subjects.Group', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Група')
    specialty = models.CharField(max_length=100, verbose_name='Спеціальність')
    year_of_study = models.PositiveIntegerField(verbose_name='Рік навчання')
    student_card_no = models.CharField(max_length=20, unique=True, verbose_name='Номер студентського')

    def __str__(self):
        return f"Студент: {self.user.get_full_name()}"