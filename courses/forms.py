# courses/forms.py

from django import forms
from .models import Course, CourseMaterial, Feedback, Enrollment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title

    def clean_description(self):
        # allow blank, but if provided, strip whitespace
        desc = self.cleaned_data.get("description")
        return (desc or "").strip()


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ["title", "file"]

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title

    def clean_file(self):
        """
        Model-level validators will run automatically too, but this ensures
        form errors appear nicely on the field.
        """
        f = self.cleaned_data.get("file")
        if not f:
            raise forms.ValidationError("Please choose a file to upload.")
        return f


class FeedbackForm(forms.ModelForm):
    """
    Pass student and course from the view:
      form = FeedbackForm(request.POST, student=request.user, course=course)
    """
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

    class Meta:
        model = Feedback
        fields = ["rating", "comment"]

    def __init__(self, *args, student=None, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        self.course = course

    def clean_comment(self):
        comment = (self.cleaned_data.get("comment") or "").strip()
        if comment and len(comment) < 3:
            raise forms.ValidationError("Comment is too short.")
        if len(comment) > 1000:
            raise forms.ValidationError("Comment is too long (max 1000 characters).")
        return comment

    def clean(self):
        cleaned = super().clean()

        # If you don't pass these, we skip enrollment checks (keeps admin/forms reusable)
        if not self.student or not self.course:
            return cleaned

        # enforce enrollment + not blocked
        try:
            enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        except Enrollment.DoesNotExist:
            raise forms.ValidationError("You must be enrolled to leave feedback.")

        if enrollment.is_blocked:
            raise forms.ValidationError("You are blocked from this course.")

        return cleaned
