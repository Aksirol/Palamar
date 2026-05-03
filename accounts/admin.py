from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Student, Teacher


# 1. Налаштування користувача (залишаємо як було)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('role', 'photo')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')


admin.site.register(User, CustomUserAdmin)


# 2. Створюємо кастомний фільтр для пошуку "Новачків"
class GroupStatusFilter(admin.SimpleListFilter):
    title = 'Статус підтвердження'
    parameter_name = 'group_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', '⏳ Очікують підтвердження (Без групи)'),
            ('confirmed', '✅ Підтверджені (З групою)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(group__isnull=True)
        if self.value() == 'confirmed':
            return queryset.filter(group__isnull=False)
        return queryset


# 3. Перетворюємо адмінку Студента на "Пункт управління"
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Які колонки показувати в таблиці
    list_display = ('get_full_name', 'user_email', 'group', 'specialty', 'year_of_study', 'student_card_no')

    # Додаємо наш кастомний фільтр
    list_filter = (GroupStatusFilter, 'group', 'year_of_study')
    search_fields = ('user__last_name', 'user__first_name', 'user__email', 'student_card_no')

    # МАГІЯ: Дозволяємо адміну змінювати ці поля прямо в списку (не заходячи в профіль)
    list_editable = ('group', 'specialty', 'year_of_study', 'student_card_no')

    # Оптимізація запитів (щоб не було N+1 в адмінці)
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'group')

    # Зручне відображення імені та email
    def get_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"

    get_full_name.short_description = 'ПІБ'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


# 4. Трохи покращимо і викладачів
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'department', 'academic_degree')
    search_fields = ('user__last_name', 'user__first_name', 'department')
    list_editable = ('department', 'academic_degree')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = 'ПІБ'