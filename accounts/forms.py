from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, StatusUpdate

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        label="Email address (optional)",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["photo"].label = "Profile photo (optional)"
        self.fields["photo"].required = False
        self.fields["photo"].widget.attrs.update(
            {
                "accept": "image/*",
            }
        )

RegisterForm = CustomUserCreationForm

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write a status update...",
                }
            ),
        }
