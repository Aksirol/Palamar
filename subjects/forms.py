from django import forms
from .models import Group, Subject

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'faculty', 'year_formed']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'credits', 'semester', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }