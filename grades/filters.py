import django_filters
from django import forms
from .models import Grade

class GradeFilter(django_filters.FilterSet):
    # Додаємо зручні календарики для вибору дат
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte', label='З дати', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte', label='По дату', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Grade
        fields = ['subject', 'type']