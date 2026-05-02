from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from accounts.mixins import TeacherRequiredMixin
from .models import Schedule
from .forms import ScheduleForm


class ScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'raw_schedule'  # Це буде сирий QuerySet

    def get_queryset(self):
        user = self.request.user

        if user.role == 'student':
            qs = Schedule.objects.filter(group=user.student_profile.group).select_related('subject', 'teacher__user',
                                                                                          'group')
        elif user.role == 'teacher':
            qs = Schedule.objects.filter(teacher=user.teacher_profile).select_related('subject', 'teacher__user',
                                                                                      'group')
        else:
            qs = Schedule.objects.all().select_related('subject', 'teacher__user', 'group')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        qs = self.object_list  # Отримуємо QuerySet з get_queryset

        # Групуємо заняття по днях
        schedule_data = []
        for day_num, day_name in Schedule.DAYS_OF_WEEK:
            lessons = qs.filter(day_of_week=day_num)
            if lessons.exists() or user.role in ['admin', 'teacher'] or user.is_superuser:
                schedule_data.append({
                    'day_name': day_name,
                    'lessons': lessons
                })

        # Передаємо згруповані дані в шаблон
        context['schedule_data'] = schedule_data
        return context


class ScheduleCreateView(TeacherRequiredMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'subjects/form.html'  # Перевикористовуємо наш універсальний шаблон!
    success_url = reverse_lazy('schedule_list')
    success_message = "Заняття успішно додано до розкладу!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Додати заняття'
        return context


class ScheduleUpdateView(TeacherRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'subjects/form.html'
    success_url = reverse_lazy('schedule_list')
    success_message = "Заняття успішно оновлено!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редагувати заняття'
        return context


class ScheduleDeleteView(TeacherRequiredMixin, DeleteView):
    model = Schedule
    template_name = 'subjects/confirm_delete.html'
    success_url = reverse_lazy('schedule_list')

    def form_valid(self, form):
        messages.success(self.request, "Заняття видалено з розкладу.")
        return super().form_valid(form)