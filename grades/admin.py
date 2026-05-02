from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'value', 'type', 'date', 'teacher')
    list_filter = ('type', 'subject', 'date')
    search_fields = ('student__user__last_name', 'subject__name')