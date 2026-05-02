from django.contrib.auth.mixins import UserPassesTestMixin

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Тепер доступ є, якщо ти викладач, адмін, АБО системний суперкористувач
        return self.request.user.is_authenticated and (
            self.request.user.role in ['teacher', 'admin'] or self.request.user.is_superuser
        )

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'student'