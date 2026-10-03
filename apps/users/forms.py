from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'bio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Роль администратора нельзя выбрать при самостоятельной регистрации.
        # Её выдаёт суперпользователь через админку Django.
        self.fields['role'].choices = [
            (value, label)
            for value, label in CustomUser.Role.choices
            if value != CustomUser.Role.ADMIN
        ]
        self.fields['bio'].widget.attrs['rows'] = 3


class ProfileForm(forms.ModelForm):
    """Редактирование собственного профиля. Роль здесь изменить нельзя."""

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'bio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs['rows'] = 5
