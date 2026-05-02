import json
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Avg
from django.template.loader import render_to_string
from weasyprint import HTML

from accounts.mixins import StudentRequiredMixin
from grades.models import Grade


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