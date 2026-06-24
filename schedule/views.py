from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from accounts.mixins import TeacherRequiredMixin
from subjects.models import Group, Subject
from .models import Schedule
from .forms import ScheduleForm


class ScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'raw_schedule'

    def get_queryset(self):
        user = self.request.user

        if user.role == 'student':
            qs = Schedule.objects.filter(
                group=user.student_profile.group
            ).select_related('subject', 'teacher__user', 'group')
        elif user.role == 'teacher':
            qs = Schedule.objects.filter(
                teacher=user.teacher_profile
            ).select_related('subject', 'teacher__user', 'group')
        else:
            qs = Schedule.objects.all().select_related('subject', 'teacher__user', 'group')

        # Фільтр по групі (тільки для адміна/викладача)
        group_id   = self.request.GET.get('group')
        subject_id = self.request.GET.get('subject')
        lesson_type = self.request.GET.get('lesson_type')

        if group_id and (user.role == 'admin' or user.is_superuser):
            qs = qs.filter(group_id=group_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if lesson_type:
            qs = qs.filter(lesson_type=lesson_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        qs   = self.object_list

        # Групуємо по днях тижня
        schedule_data = []
        for day_num, day_name in Schedule.DAYS_OF_WEEK:
            lessons = qs.filter(day_of_week=day_num)
            if lessons.exists() or user.role in ['admin', 'teacher'] or user.is_superuser:
                schedule_data.append({
                    'day_name': day_name,
                    'lessons':  lessons,
                })

        context['schedule_data'] = schedule_data

        # Дані для форми фільтрації (тільки адмін бачить фільтр по групах)
        if user.is_superuser or user.role == 'admin':
            context['groups']   = Group.objects.all()
        context['subjects']      = Subject.objects.all()
        context['lesson_types']  = Schedule.LESSON_TYPES
        context['selected_group']       = self.request.GET.get('group', '')
        context['selected_subject']     = self.request.GET.get('subject', '')
        context['selected_lesson_type'] = self.request.GET.get('lesson_type', '')
        return context


class ScheduleCreateView(TeacherRequiredMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'subjects/form.html'
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
