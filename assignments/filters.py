import django_filters
from django import forms
from .models import Assignment

class AssignmentFilter(django_filters.FilterSet):

    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Назва завдання',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук за назвою...',
        })
    )

    deadline_from = django_filters.DateFilter(
        field_name='deadline', lookup_expr='gte', label='Дедлайн від',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    deadline_to = django_filters.DateFilter(
        field_name='deadline', lookup_expr='lte', label='Дедлайн до',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ('deadline', 'deadline'),
            ('title',    'title'),
        ),
        field_labels={
            'deadline':  'За дедлайном (зростання)',
            '-deadline': 'За дедлайном (спадання)',
            'title':     'За назвою (А-Я)',
            '-title':    'За назвою (Я-А)',
        },
        label='Сортування'
        # widget=forms.Select() звідси ПРИБРАНО
    )

    class Meta:
        model = Assignment
        fields = ['subject']
        # Блок widgets звідси ПРИБРАНО

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамічно додаємо клас 'form-select' до всіх випадаючих списків
        for field_name, field in self.form.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})