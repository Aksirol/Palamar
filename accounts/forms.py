from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'photo')

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        # Перевіряємо, чи фото існує І чи є воно файлом (має атрибут 'size')
        if photo and hasattr(photo, 'size'):
            # Обмеження у 2 МБ (2 * 1024 * 1024 байт)
            if photo.size > 2 * 1024 * 1024:
                raise ValidationError("Розмір фото не повинен перевищувати 2 МБ.")
        return photo