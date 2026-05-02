from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Attendance(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, verbose_name='Студент')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, verbose_name='Предмет')
    date = models.DateField(default=timezone.now, verbose_name='Дата')
    is_present = models.BooleanField(default=True, verbose_name='Присутній')
    reason = models.CharField(max_length=255, blank=True, null=True, verbose_name='Причина відсутності')

    class Meta:
        verbose_name = 'Відвідуваність'
        verbose_name_plural = 'Відвідуваність'
        # Запобігаємо дублям на рівні БД
        unique_together = ['student', 'subject', 'date']
        ordering = ['-date', 'student__user__last_name']

    def clean(self):
        super().clean()
        if self.date > timezone.now().date():
            raise ValidationError("Не можна відмічати відвідуваність на майбутню дату.")

    def __str__(self):
        status = "+" if self.is_present else "-"
        return f"{self.student.user.last_name} | {self.subject.name} | {self.date} [{status}]"