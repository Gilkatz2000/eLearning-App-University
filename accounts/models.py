from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"

    class Themes(models.TextChoices):
        DEFAULT = "default", "Default"
        MIDNIGHT = "midnight", "Midnight"
        EMERALD = "emerald", "Emerald"
        SUNSET = "sunset", "Sunset"
        LIGHT = "light", "Light"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    # NEW: user theme preference
    theme = models.CharField(max_length=20, choices=Themes.choices, default=Themes.DEFAULT)

    def is_student(self):
        return self.role == self.Roles.STUDENT

    def is_teacher(self):
        return self.role == self.Roles.TEACHER


class StatusUpdate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="status_updates",
    )
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status by {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"
