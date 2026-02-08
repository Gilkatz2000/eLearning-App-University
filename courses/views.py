from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import teacher_required, student_required
from notifications.models import Notification
from .forms import CourseForm
from django.utils import timezone
from .models import Course, Enrollment

@teacher_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("my_courses")
    else:
        form = CourseForm()
    return render(request, "courses/create_course.html", {"form": form})

@student_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    if created:
        Notification.objects.create(
            to_user=course.teacher,
            text=f"{request.user.username} enrolled in your course '{course.title}'"
        )

    return redirect("course_detail", course_id=course.id)
