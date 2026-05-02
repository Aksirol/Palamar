from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from accounts.mixins import TeacherRequiredMixin
from .models import Subject, Group
from .forms import SubjectForm, GroupForm


# --- CRUD для Предметів (Subjects) ---

class SubjectListView(ListView):
    model = Subject
    template_name = 'subjects/subject_list.html'
    context_object_name = 'subjects'


class SubjectCreateView(TeacherRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/form.html'
    success_url = reverse_lazy('subject_list')
    success_message = "Предмет успішно додано!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Додати предмет'
        return context


class SubjectUpdateView(TeacherRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/form.html'
    success_url = reverse_lazy('subject_list')
    success_message = "Предмет успішно оновлено!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редагувати предмет'
        return context


class SubjectDeleteView(TeacherRequiredMixin, DeleteView):
    model = Subject
    template_name = 'subjects/confirm_delete.html'
    success_url = reverse_lazy('subject_list')

    def form_valid(self, form):
        messages.success(self.request, "Предмет успішно видалено.")
        return super().form_valid(form)


# --- CRUD для Груп (Groups) ---
# (Логіка ідентична, тільки для моделі Group)

class GroupListView(ListView):
    model = Group
    template_name = 'subjects/group_list.html'
    context_object_name = 'groups'


class GroupCreateView(TeacherRequiredMixin, SuccessMessageMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'subjects/form.html'
    success_url = reverse_lazy('group_list')
    success_message = "Групу успішно додано!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Додати групу'
        return context


class GroupUpdateView(TeacherRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'subjects/form.html'
    success_url = reverse_lazy('group_list')
    success_message = "Групу успішно оновлено!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редагувати групу'
        return context


class GroupDeleteView(TeacherRequiredMixin, DeleteView):
    model = Group
    template_name = 'subjects/confirm_delete.html'
    success_url = reverse_lazy('group_list')

    def form_valid(self, form):
        messages.success(self.request, "Групу успішно видалено.")
        return super().form_valid(form)