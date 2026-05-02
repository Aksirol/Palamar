from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm


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