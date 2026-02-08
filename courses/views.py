from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import teacher_required, student_required
from notifications.models import Notification

from .forms import CourseForm
from .models import Course, Enrollment


@teacher_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("course_list")  # <-- changed from my_courses to course_list
    else:
        form = CourseForm()
    return render(request, "courses/create_course.html", {"form": form})


@login_required
def course_list(request):
    courses = Course.objects.order_by("-created_at")
    return render(request, "courses/course_list.html", {"courses": courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment = None
    if request.user.is_authenticated and request.user.is_student():
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()

    return render(
        request,
        "courses/course_detail.html",
        {"course": course, "enrollment": enrollment},
    )


@student_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
    )

    # Enforce blocked students
    if enrollment.is_blocked:
        return redirect("course_detail", course_id=course.id)

    # Notify teacher only on first-time enrollment
    if created:
        Notification.objects.create(
            to_user=course.teacher,
            text=f"{request.user.username} enrolled in your course '{course.title}'",
        )

    return redirect("course_detail", course_id=course.id)
