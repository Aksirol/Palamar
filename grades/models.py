from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Grade(models.Model):
    GRADE_TYPES = [
        ('current', 'Поточна'),
        ('module', 'Модульна'),
        ('exam', 'Іспит'),
        ('credit', 'Залік'),
    ]

    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, verbose_name='Студент')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, verbose_name='Предмет')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Викладач')

    # Оцінка від 1 до 100
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Оцінка (1-100)'
    )

    type = models.CharField(max_length=20, choices=GRADE_TYPES, default='current', verbose_name='Тип оцінки')
    date = models.DateField(default=timezone.now, verbose_name='Дата виставлення')
    comment = models.TextField(blank=True, null=True, verbose_name='Коментар')

    class Meta:
        verbose_name = 'Оцінка'
        verbose_name_plural = 'Оцінки'
        ordering = ['-date', '-id']

    def clean(self):
        super().clean()
        # Бізнес-логіка: Лише один Іспит або Залік по предмету для студента
        if self.type in ['exam', 'credit']:
            existing_grades = Grade.objects.filter(
                student=self.student,
                subject=self.subject,
                type=self.type
            ).exclude(pk=self.pk)  # Виключаємо поточний запис (щоб працювало редагування)

            if existing_grades.exists():
                raise ValidationError(f"Цей студент вже має оцінку типу '{self.get_type_display()}' з цього предмета.")

    def __str__(self):
        return f"{self.student.user.last_name} - {self.subject.name} - {self.value}"