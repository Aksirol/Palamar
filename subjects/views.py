from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from accounts.mixins import TeacherRequiredMixin
from .models import Subject, Group
from .forms import SubjectForm, GroupForm


# ══════════════════════════════════════════════
#  ПРЕДМЕТИ (Subjects)
# ══════════════════════════════════════════════

class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'subjects/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 10

    def get_queryset(self):
        qs = Subject.objects.all()

        # Пошук за назвою
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)

        # Фільтр за семестром
        semester = self.request.GET.get('semester', '').strip()
        if semester:
            qs = qs.filter(semester=semester)

        # Сортування
        ordering = self.request.GET.get('ordering', 'semester')
        allowed  = ['semester', '-semester', 'name', '-name', 'credits', '-credits']
        if ordering in allowed:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q']        = self.request.GET.get('q', '')
        context['semester'] = self.request.GET.get('semester', '')
        context['ordering'] = self.request.GET.get('ordering', 'semester')
        # Для випадаючого списку семестрів
        context['semesters'] = Subject.objects.values_list(
            'semester', flat=True
        ).distinct().order_by('semester')
        return context


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


# ══════════════════════════════════════════════
#  ГРУПИ (Groups)
# ══════════════════════════════════════════════

class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'subjects/group_list.html'
    context_object_name = 'groups'
    paginate_by = 10

    def get_queryset(self):
        qs = Group.objects.all()

        # Пошук за назвою або факультетом
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(faculty__icontains=q)

        # Сортування
        ordering = self.request.GET.get('ordering', '-year_formed')
        allowed  = ['name', '-name', 'year_formed', '-year_formed', 'faculty', '-faculty']
        if ordering in allowed:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q']        = self.request.GET.get('q', '')
        context['ordering'] = self.request.GET.get('ordering', '-year_formed')
        return context


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
