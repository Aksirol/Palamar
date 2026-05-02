from django.contrib import admin
from .models import Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'subject', 'teacher', 'get_day_of_week_display', 'start_time', 'room')
    list_filter = ('day_of_week', 'group', 'teacher')