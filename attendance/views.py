import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from accounts.mixins import TeacherRequiredMixin, StudentRequiredMixin
from schedule.models import Schedule
from subjects.models import Group, Subject
from accounts.models import Student
from .models import Attendance


# 1. МАОВА ВІДМІТКА ВІДВІДУВАНОСТІ (Для Викладачів)
class AttendanceMarkView(TeacherRequiredMixin, View):
    template_name = 'attendance/mark_attendance.html'

    def get(self, request):
        # Отримуємо параметри з URL (якщо викладач вже обрав їх)
        group_id = request.GET.get('group')
        subject_id = request.GET.get('subject')
        date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))

        groups = Group.objects.all()
        subjects = Subject.objects.all()

        # students_with_state — список dict з готовим станом для кожного студента.
        # Це виправляє баг шаблону, де вкладений {% for key, record in existing_data.items %}
        # не міг знайти потрібного студента і всі чекбокси скидались в unchecked.
        students_with_state = []

        if group_id and subject_id:
            students_qs = Student.objects.filter(
                group_id=group_id
            ).select_related('user').order_by('user__last_name')

            # Один запит для всіх записів відвідуваності за цей день
            records = Attendance.objects.filter(
                student__group_id=group_id,
                subject_id=subject_id,
                date=date_str
            )
            # Словник {student_id: record} — O(1) пошук у шаблоні
            existing_map = {r.student_id: r for r in records}

            for student in students_qs:
                record = existing_map.get(student.pk)
                students_with_state.append({
                    'student':    student,
                    # Якщо запису немає (нова/не відмічена дата) → за замовчуванням "присутній"
                    'is_present': record.is_present if record is not None else True,
                    'reason':     record.reason     if record is not None else '',
                })

        return render(request, self.template_name, {
            'groups': groups,
            'subjects': subjects,
            'selected_group':   int(group_id)   if group_id   else None,
            'selected_subject': int(subject_id) if subject_id else None,
            'selected_date': date_str,
            'students_with_state': students_with_state,
        })

    def post(self, request):
        group_id = request.POST.get('group')
        subject_id = request.POST.get('subject')
        date_str = request.POST.get('date')

        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Неправильний формат дати.")
            return redirect(request.path)

        # Валідація майбутньої дати
        if date_obj > timezone.now().date():
            messages.error(request, "Не можна відмічати відвідуваність на майбутню дату.")
            return redirect(f"{request.path}?group={group_id}&subject={subject_id}&date={date_str}")

        students = Student.objects.filter(group_id=group_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Проходимося по кожному студенту групи і зберігаємо/оновлюємо дані
        for student in students:
            # Чекбокс передає значення "on", якщо відмічений
            is_present = request.POST.get(f'status_{student.pk}') == 'on'
            reason = request.POST.get(f'reason_{student.pk}', '').strip()

            # МАГІЯ DJANGO: update_or_create створює запис, якщо його нема,
            # або оновлює існуючий, якщо він вже є для цього студента/предмета/дати
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=date_obj,
                defaults={
                    'is_present': is_present,
                    'reason': reason if not is_present else ''  # Очищаємо причину, якщо присутній
                }
            )

        messages.success(request, f"Відвідуваність за {date_str} успішно збережена!")
        return redirect(f"{request.path}?group={group_id}&subject={subject_id}&date={date_str}")


# 2. СТАТИСТИКА ВІДВІДУВАНОСТІ (Для Студентів)
class AttendanceStatsView(StudentRequiredMixin, View):
    template_name = 'attendance/stats.html'

    def get(self, request):
        student = request.user.student_profile
        # Знаходимо всі предмети, з яких студент має хоча б одну відмітку
        subjects = Subject.objects.filter(attendance__student=student).distinct()

        stats = []
        for subject in subjects:
            records = Attendance.objects.filter(student=student, subject=subject)
            total = records.count()
            present = records.filter(is_present=True).count()

            # Рахуємо відсоток
            percentage = (present / total * 100) if total > 0 else 0

            stats.append({
                'subject': subject,
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': round(percentage, 1),
                'warning': percentage < 75.0  # Прапорець для підсвітки червоним у шаблоні
            })

        return render(request, self.template_name, {'stats': stats})


class TeacherAttendanceStatsView(TeacherRequiredMixin, View):
    template_name = 'attendance/teacher_stats.html'

    def get(self, request):
        user = request.user
        # .distinct('group', 'subject') — PostgreSQL-only синтаксис, не працює в SQLite.
        # Замінено на values() + distinct() який працює у всіх СУБД.
        if user.is_superuser or user.role == 'admin':
            schedule_pairs = (
                Schedule.objects
                .values('group_id', 'subject_id')
                .distinct()
                .select_related()
            )
            # Отримуємо повноцінні об'єкти для шаблону
            seen = set()
            schedules = []
            for entry in Schedule.objects.select_related('group', 'subject').all():
                key = (entry.group_id, entry.subject_id)
                if key not in seen:
                    seen.add(key)
                    schedules.append(entry)
        else:
            teacher = user.teacher_profile
            seen = set()
            schedules = []
            for entry in teacher.schedule_set.select_related('group', 'subject').all():
                key = (entry.group_id, entry.subject_id)
                if key not in seen:
                    seen.add(key)
                    schedules.append(entry)

        return render(request, self.template_name, {'schedules': schedules})