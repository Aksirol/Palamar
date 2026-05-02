import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# Функція для унікальних імен файлів
def submission_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'submissions/{uuid.uuid4()}.{ext}'


class Assignment(models.Model):
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, verbose_name='Предмет')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Викладач')
    title = models.CharField(max_length=200, verbose_name='Назва завдання')
    description = models.TextField(verbose_name='Опис завдання')
    deadline = models.DateTimeField(verbose_name='Дедлайн')
    max_score = models.PositiveIntegerField(default=100, verbose_name='Максимальний бал')

    class Meta:
        verbose_name = 'Завдання'
        verbose_name_plural = 'Завдання'
        ordering = ['-deadline']

    def __str__(self):
        return f"{self.title} ({self.subject.name})"


class Submission(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Призначено'),  # Технічно статус до здачі
        ('submitted', 'Здано'),
        ('checked', 'Перевірено'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions',
                                   verbose_name='Завдання')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, verbose_name='Студент')

    file = models.FileField(upload_to=submission_path, blank=True, null=True, verbose_name='Файл з відповіддю')
    text_answer = models.TextField(blank=True, null=True, verbose_name='Текстова відповідь')

    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Час здачі')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted', verbose_name='Статус')
    score = models.PositiveIntegerField(blank=True, null=True, verbose_name='Оцінка')

    class Meta:
        verbose_name = 'Здана робота'
        verbose_name_plural = 'Здані роботи'
        unique_together = ['assignment',
                           'student']  # Студент може здати одне завдання лише один раз (або оновлювати існуюче)

    def clean(self):
        super().clean()

        # 1. Перевірка дедлайну
        # (Перевіряємо hasattr, щоб уникнути помилки при валідації нової пустої форми)
        if hasattr(self, 'assignment') and self.assignment_id is not None:
            if self.status == 'submitted':
                if timezone.now() > self.assignment.deadline:
                    raise ValidationError("Дедлайн минув. Здача або редагування роботи заблоковані.")

        # 2. Однонаправлений флоу статусів (не даємо повернути 'checked' назад)
        if self.pk:
            old_status = Submission.objects.get(pk=self.pk).status
            if old_status == 'checked' and self.status in ['assigned', 'submitted']:
                raise ValidationError("Неможливо скасувати перевірку. Робота вже перевірена.")

        # 3. Перевірка наявності хоч якоїсь відповіді
        if not self.file and not self.text_answer:
            raise ValidationError("Необхідно прикріпити файл або написати текстову відповідь.")

    def __str__(self):
        return f"{self.student.user.last_name} - {self.assignment.title}"