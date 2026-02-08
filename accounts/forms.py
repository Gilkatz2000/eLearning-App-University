from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Roles.choices)

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")


class LoginForm(AuthenticationForm):
    pass
