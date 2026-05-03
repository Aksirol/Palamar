import json
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Avg
from django.template.loader import render_to_string
from weasyprint import HTML

from accounts.mixins import StudentRequiredMixin
from grades.models import Grade
from subjects.models import Group
from schedule.models import Schedule
from accounts.mixins import TeacherRequiredMixin


class StudentDashboardView(StudentRequiredMixin, View):
    template_name = 'reports/dashboard.html'

    def get(self, request):
        student = request.user.student_profile

        # Агрегація бази даних: середній бал по кожному предмету
        grades_agg = Grade.objects.filter(student=student).values('subject__name').annotate(avg_score=Avg('value'))

        # Готуємо дані для Chart.js
        labels = [item['subject__name'] for item in grades_agg]
        # Округлюємо до 1 знака після коми, або ставимо 0
        data = [round(float(item['avg_score']), 1) if item['avg_score'] else 0 for item in grades_agg]

        chart_data = {
            'labels': labels,
            'data': data
        }

        return render(request, self.template_name, {
            'chart_data_json': json.dumps(chart_data),  # Передаємо JSON у контекст
            'student': student
        })


class DownloadPDFReportView(StudentRequiredMixin, View):
    def get(self, request):
        student = request.user.student_profile

        # Отримуємо всі оцінки студента (вирішуємо N+1)
        grades = Grade.objects.filter(student=student).select_related('subject', 'teacher__user').order_by('-date')

        # Загальний середній бал
        overall_avg = grades.aggregate(avg=Avg('value'))['avg']
        overall_avg = round(overall_avg, 2) if overall_avg else 0

        context = {
            'student': student,
            'grades': grades,
            'overall_avg': overall_avg
        }

        # 1. Рендеримо наш спеціальний HTML для PDF
        html_string = render_to_string('reports/pdf_report.html', context)

        # 2. Конвертуємо HTML у PDF через WeasyPrint
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        # 3. Повертаємо PDF як відповідь браузеру (ліниво)
        response = HttpResponse(pdf, content_type='application/pdf')
        # inline - відкриє в браузері. attachment - почне завантаження.
        response['Content-Disposition'] = f'inline; filename="transcript_{student.user.username}.pdf"'
        return response


class TeacherGroupStatsView(TeacherRequiredMixin, View):
    template_name = 'reports/teacher_dashboard.html'

    def get(self, request):
        user = request.user
        selected_group_id = request.GET.get('group')

        # 1. Визначаємо, які групи може бачити користувач
        if user.is_superuser:
            groups = Group.objects.all()
        else:
            # Викладач бачить лише ті групи, де має заняття в розкладі
            teacher_profile = user.teacher_profile
            group_ids = Schedule.objects.filter(teacher=teacher_profile).values_list('group_id', flat=True).distinct()
            groups = Group.objects.filter(id__in=group_ids)

        chart_data = None
        students_stats = []
        selected_group = None

        # Якщо користувач обрав групу з випадаючого списку
        if selected_group_id:
            selected_group = Group.objects.filter(id=selected_group_id).first()

            # Перевірка безпеки: чи дійсно він має доступ до цієї групи
            if selected_group and selected_group in groups:

                # 2. Фільтруємо оцінки: адмін бачить всі, викладач - лише зі своїх предметів
                if user.is_superuser:
                    qs = Grade.objects.filter(student__group=selected_group)
                else:
                    qs = Grade.objects.filter(student__group=selected_group, teacher=user.teacher_profile)

                # 3. Дані для графіка (середній бал по предметах у цій групі)
                subject_avg = qs.values('subject__name').annotate(avg_score=Avg('value'))
                labels = [item['subject__name'] for item in subject_avg]
                data = [round(float(item['avg_score']), 1) if item['avg_score'] else 0 for item in subject_avg]

                if labels:  # Якщо є дані, формуємо JSON
                    chart_data = json.dumps({'labels': labels, 'data': data})

                # 4. Дані для таблиці (рейтинг студентів у групі)
                student_avg = qs.values(
                    'student__user__first_name',
                    'student__user__last_name'
                ).annotate(avg_score=Avg('value')).order_by('-avg_score')

                for item in student_avg:
                    students_stats.append({
                        'name': f"{item['student__user__last_name']} {item['student__user__first_name']}",
                        'avg': round(float(item['avg_score']), 1) if item['avg_score'] else 0
                    })

        return render(request, self.template_name, {
            'groups': groups,
            'selected_group': selected_group,
            'chart_data_json': chart_data,
            'students_stats': students_stats
        })