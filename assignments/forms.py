from django import forms
from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'deadline', 'max_score']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'text_answer']
        widgets = {
            'text_answer': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Додайте текстову відповідь, якщо необхідно...'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Перевірка розміру (5 МБ)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Файл занадто великий. Максимальний розмір — 5 МБ.")

            # Перевірка розширення
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx', 'zip']:
                raise forms.ValidationError("Дозволені лише файли у форматах: .pdf, .docx, .zip.")
        return file


# Форма для викладача (виставлення оцінки)
class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['score']