from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher

# Розширюємо стандартну адмінку користувачів
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('role', 'photo')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Teacher)