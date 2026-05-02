from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'is_present', 'reason')
    list_filter = ('date', 'subject', 'is_present')
    search_fields = ('student__user__last_name', 'subject__name')