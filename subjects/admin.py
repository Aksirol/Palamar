from django.contrib import admin
from .models import Group, Subject

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'year_formed')
    list_filter = ('faculty', 'year_formed')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'credits', 'semester')
    list_filter = ('semester',)
    search_fields = ('name',)