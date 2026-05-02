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
    context_object_name = 'schedule_data'  # Передаємо згруповані дані

    def get_queryset(self):
        user = self.request.user

        # Отримуємо QuerySet залежно від ролі + select_related (вирішення N+1)
        if user.role == 'student':
            qs = Schedule.objects.filter(group=user.student_profile.group).select_related('subject', 'teacher__user',
                                                                                          'group')
        elif user.role == 'teacher':
            qs = Schedule.objects.filter(teacher=user.teacher_profile).select_related('subject', 'teacher__user',
                                                                                      'group')
        else:  # Адміністратор бачить все
            qs = Schedule.objects.all().select_related('subject', 'teacher__user', 'group')

        # Групуємо заняття по днях (створюємо список словників для зручності в шаблоні)
        schedule_data = []
        for day_num, day_name in Schedule.DAYS_OF_WEEK:
            lessons = qs.filter(day_of_week=day_num)
            if lessons.exists() or user.role in ['admin', 'teacher']:
                # Показуємо день, якщо є уроки, або якщо це вчитель (щоб міг додати)
                schedule_data.append({
                    'day_name': day_name,
                    'lessons': lessons
                })

        return schedule_data


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