from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from subjects.models import Group
from .models import Student


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Невірний логін або пароль.")
        return super().form_invalid(form)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Адмін має прив'язати групу пізніше
            messages.success(request,
                             f"Акаунт {user.username} успішно створено! Зачекайте на підтвердження групи адміністратором.")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')  # Замінимо 'home' на твою головну сторінку
        else:
            messages.error(request, "Помилка при реєстрації. Перевірте введені дані.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


class PendingStudentsView(UserPassesTestMixin, View):
    template_name = 'accounts/pending_students.html'

    # Перевірка доступу: пускаємо лише адміністраторів (суперюзерів або з role='admin')
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_superuser or user.role == 'admin')

    def get(self, request):
        # Шукаємо студентів, у яких group = null
        pending_students = Student.objects.filter(group__isnull=True).select_related('user')
        groups = Group.objects.all()

        return render(request, self.template_name, {
            'pending_students': pending_students,
            'groups': groups
        })

    def post(self, request):
        student_id = request.POST.get('student_id')
        group_id = request.POST.get('group_id')
        specialty = request.POST.get('specialty')
        year_of_study = request.POST.get('year_of_study')
        student_card_no = request.POST.get('student_card_no')

        if student_id and group_id:
            student = get_object_or_404(Student, pk=student_id)
            group = get_object_or_404(Group, pk=group_id)

            # Оновлюємо дані студента
            student.group = group
            student.specialty = specialty.strip() if specialty else 'Не вказано'
            student.year_of_study = int(year_of_study) if year_of_study else 1
            student.student_card_no = student_card_no.strip() if student_card_no else f'TEMP-{student.pk}'
            student.save()

            messages.success(request,
                             f"Студента {student.user.get_full_name()} успішно зараховано до групи {group.name}!")
        else:
            messages.error(request, "Помилка! Необхідно обрати групу.")

        return redirect('pending_students')