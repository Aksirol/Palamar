from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import TeacherRequiredMixin, StudentRequiredMixin
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm
from .filters import AssignmentFilter


# --- ЗАВДАННЯ ---

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            group = user.student_profile.group
            qs = Assignment.objects.filter(
                subject__schedule__group=group
            ).distinct().select_related('subject', 'teacher__user')
        elif user.role == 'teacher':
            qs = Assignment.objects.filter(
                teacher=user.teacher_profile
            ).select_related('subject')
        else:
            qs = Assignment.objects.none()

        # Застосовуємо фільтр
        self.filterset = AssignmentFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class AssignmentCreateView(TeacherRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'subjects/form.html'
    success_url = reverse_lazy('assignment_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Завдання успішно створено!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Створити завдання'
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin'):
            messages.info(request, "Адміністратори створюють завдання через панель адміністратора.")
            return redirect('admin:assignments_assignment_add')
        return super().dispatch(request, *args, **kwargs)


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['now'] = timezone.now()

        if user.role == 'student':
            student = user.student_profile
            submission = Submission.objects.filter(
                assignment=self.object, student=student
            ).first()
            context['submission'] = submission
            if not submission or submission.status == 'submitted':
                context['form'] = SubmissionForm(instance=submission)

        elif user.role == 'teacher':
            context['submissions'] = self.object.submissions.all().select_related('student__user')

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        if user.role == 'student':
            if timezone.now() > self.object.deadline:
                messages.error(request, "Дедлайн минув!")
                return redirect('assignment_detail', pk=self.object.pk)

            student = user.student_profile
            submission = Submission.objects.filter(
                assignment=self.object, student=student
            ).first()

            form = SubmissionForm(request.POST, request.FILES, instance=submission)
            if form.is_valid():
                sub = form.save(commit=False)
                sub.assignment = self.object
                sub.student    = student
                sub.status     = 'submitted'
                sub.save()
                messages.success(request, "Роботу успішно здано!")
            else:
                messages.error(request, "Помилка! Перевірте формат та розмір файлу.")

            return redirect('assignment_detail', pk=self.object.pk)

        return self.get(request, *args, **kwargs)


# --- ПЕРЕВІРКА ВИКЛАДАЧЕМ ---

class GradeSubmissionView(TeacherRequiredMixin, UpdateView):
    model = Submission
    form_class = GradeSubmissionForm
    template_name = 'subjects/form.html'

    def form_valid(self, form):
        if form.cleaned_data.get('score') is not None:
            form.instance.status = 'checked'
            messages.success(self.request, "Роботу перевірено та оцінено!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('assignment_detail', kwargs={'pk': self.object.assignment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Оцінити роботу: {self.object.student.user.get_full_name()}'
        return context
