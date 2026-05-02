from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from accounts.mixins import TeacherRequiredMixin
from schedule.models import Schedule
from .models import Grade
from .forms import GradeForm
from .filters import GradeFilter
from django.shortcuts import redirect


class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'grades/grade_list.html'
    context_object_name = 'grades'
    paginate_by = 20  # Пагінація!

    def get_queryset(self):
        user = self.request.user

        # Використовуємо select_related для всіх ForeignKey (N+1 проблема вирішена)
        qs = Grade.objects.select_related('student__user', 'subject', 'teacher__user')

        if user.role == 'student':
            qs = qs.filter(student=user.student_profile)
        elif user.role == 'teacher':
            qs = qs.filter(teacher=user.teacher_profile)

        # Застосовуємо фільтр
        self.filterset = GradeFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Передаємо форму фільтра в шаблон
        return context


class GradeCreateView(TeacherRequiredMixin, SuccessMessageMixin, CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'subjects/form.html'  # Знову наш універсальний шаблон
    success_url = reverse_lazy('grade_list')
    success_message = "Оцінку успішно виставлено!"

    def dispatch(self, request, *args, **kwargs):
        # Якщо це адмін (суперкористувач), зручно перенаправляємо його в Django Admin
        if request.user.is_authenticated and request.user.is_superuser:
            messages.info(request, "Адміністратори виставляють оцінки через цю панель.")
            return redirect('admin:grades_grade_add')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Виставити оцінку'
        return context

    def form_valid(self, form):
        user = self.request.user

        # Якщо оцінку ставить викладач
        if user.role == 'teacher':
            teacher_profile = user.teacher_profile
            form.instance.teacher = teacher_profile

            student = form.cleaned_data['student']
            subject = form.cleaned_data['subject']

            # БІЗНЕС-ЛОГІКА: Перевіряємо чи веде цей викладач предмет у групі студента
            if student.group:
                has_permission = Schedule.objects.filter(
                    teacher=teacher_profile,
                    group=student.group,
                    subject=subject
                ).exists()

                if not has_permission:
                    form.add_error(None,
                                   "Помилка доступу: Ви не ведете цей предмет у групі цього студента згідно з розкладом.")
                    return self.form_invalid(form)
            else:
                form.add_error('student', "У студента не вказана група.")
                return self.form_invalid(form)

        return super().form_valid(form)