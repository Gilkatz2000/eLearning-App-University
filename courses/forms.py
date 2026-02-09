from django import forms
from .models import Course, CourseMaterial, Feedback


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ["title", "file"]


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comment"]

    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        initial=5,
        label="Rating (1-5)",
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Comment (optional)",
    )
