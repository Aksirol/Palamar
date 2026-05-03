import django_filters
from django import forms
from .models import Grade


class GradeFilter(django_filters.FilterSet):

    # Пошук по прізвищу студента
    student_name = django_filters.CharFilter(
        field_name='student__user__last_name',
        lookup_expr='icontains',
        label='Прізвище студента',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук за прізвищем...',
        })
    )

    # Діапазон дат
    date_from = django_filters.DateFilter(
        field_name='date', lookup_expr='gte', label='З дати',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = django_filters.DateFilter(
        field_name='date', lookup_expr='lte', label='По дату',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Сортування
    ordering = django_filters.OrderingFilter(
        fields=(
            ('date',  'date'),
            ('value', 'value'),
        ),
        field_labels={
            'date':   'За датою (зростання)',
            '-date':  'За датою (спадання)',
            'value':  'За оцінкою (зростання)',
            '-value': 'За оцінкою (спадання)',
        },
        label='Сортування',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model  = Grade
        fields = ['subject', 'type']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'type':    forms.Select(attrs={'class': 'form-select'}),
        }
