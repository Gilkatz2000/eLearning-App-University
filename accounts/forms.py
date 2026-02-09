from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, StatusUpdate


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "photo", "password1", "password2"]


class LoginForm(AuthenticationForm):
    pass


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Share an update..."}),
        }
        labels = {"text": ""}
