from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Назва групи')
    faculty = models.CharField(max_length=150, verbose_name='Факультет')
    year_formed = models.PositiveIntegerField(verbose_name='Рік формування')

    class Meta:
        verbose_name = 'Група'
        verbose_name_plural = 'Групи'
        ordering = ['-year_formed', 'name']

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=150, verbose_name='Назва предмета')
    credits = models.PositiveIntegerField(verbose_name='Кредити (ECTS)')
    semester = models.PositiveIntegerField(verbose_name='Семестр')
    description = models.TextField(blank=True, null=True, verbose_name='Опис')

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предмети'
        ordering = ['semester', 'name']

    def __str__(self):
        return f"{self.name} ({self.semester} семестр)"