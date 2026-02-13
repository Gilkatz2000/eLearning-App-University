from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, StatusUpdate


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="First name")
    last_name = forms.CharField(required=True, label="Last name")

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "photo",
            "password1",
            "password2",
        ]

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Share an update..."}),
        }
        labels = {"text": ""}
