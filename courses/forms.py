from django import forms
from .models import Course, CourseMaterial


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ["title", "file"]
