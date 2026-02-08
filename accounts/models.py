from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def is_student(self):
        return self.role == self.Roles.STUDENT

    def is_teacher(self):
        return self.role == self.Roles.TEACHER
