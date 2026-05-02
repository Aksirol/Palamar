from django.db import models
from django.core.exceptions import ValidationError


class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (1, 'Понеділок'),
        (2, 'Вівторок'),
        (3, 'Середа'),
        (4, 'Четвер'),
        (5, 'П\'ятниця'),
        (6, 'Субота'),
        (7, 'Неділя'),
    )

    LESSON_TYPES = (
        ('lecture', 'Лекція'),
        ('practice', 'Практика'),
        ('lab', 'Лабораторна'),
    )

    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, verbose_name='Предмет')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, verbose_name='Викладач')
    group = models.ForeignKey('subjects.Group', on_delete=models.CASCADE, verbose_name='Група')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='День тижня')
    start_time = models.TimeField(verbose_name='Час початку')
    end_time = models.TimeField(verbose_name='Час закінчення')
    room = models.CharField(max_length=50, verbose_name='Аудиторія')
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, verbose_name='Тип заняття')

    class Meta:
        verbose_name = 'Заняття'
        verbose_name_plural = 'Розклад'
        ordering = ['day_of_week', 'start_time']

    def clean(self):
        super().clean()
        # Перевірка: чи не закінчується заняття раніше, ніж починається
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Час закінчення має бути пізніше часу початку.")

        # Базовий QuerySet для пошуку накладок (перетинання часу)
        overlapping_lessons = Schedule.objects.filter(
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)  # Виключаємо поточний запис при редагуванні

        # 1. Один викладач не може бути у двох місцях одночасно
        if overlapping_lessons.filter(teacher=self.teacher).exists():
            raise ValidationError({'teacher': "Цей викладач вже має заняття в цей час."})

        # 2. Одна аудиторія не може бути зайнята двічі
        if overlapping_lessons.filter(room=self.room).exists():
            raise ValidationError({'room': "Ця аудиторія вже зайнята в цей час."})

        # 3. Одна група не може бути на двох заняттях одночасно
        if overlapping_lessons.filter(group=self.group).exists():
            raise ValidationError({'group': "Ця група вже має заняття в цей час."})

    def __str__(self):
        return f"{self.group} - {self.subject.name} ({self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')})"