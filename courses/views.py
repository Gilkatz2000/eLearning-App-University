from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

from accounts.decorators import teacher_required, student_required
from notifications.models import Notification

from .forms import CourseForm, CourseMaterialForm, FeedbackForm
from .models import Course, Enrollment, Feedback

from django.http import FileResponse
from .models import CourseMaterial

@teacher_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("course_list")
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
    my_feedback = None
    feedback_form = None

    # Feedback list + average (visible to everyone)
    feedbacks = course.feedbacks.select_related("student").order_by("-created_at")
    avg_rating = feedbacks.aggregate(avg=Avg("rating"))["avg"]

    is_owner_teacher = (
        request.user.is_authenticated
        and request.user.is_teacher()
        and course.teacher_id == request.user.id
    )

    # Student enrollment state (used for blocking / feedback form)
    if request.user.is_authenticated and request.user.is_student():
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
        my_feedback = Feedback.objects.filter(course=course, student=request.user).first()
        feedback_form = FeedbackForm(instance=my_feedback, student=request.user, course=course)

    # ✅ Materials visibility decision (server-side)
    can_view_materials = False
    if is_owner_teacher:
        can_view_materials = True
    elif request.user.is_authenticated and request.user.is_student():
        if enrollment and not enrollment.is_blocked:
            can_view_materials = True

    # ✅ Provide filtered materials list to template
    materials = course.materials.order_by("-uploaded_at") if can_view_materials else course.materials.none()

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "enrollment": enrollment,
            "feedbacks": feedbacks,
            "avg_rating": avg_rating,
            "my_feedback": my_feedback,
            "feedback_form": feedback_form,
            "is_owner_teacher": is_owner_teacher,
            "materials": materials,
            "can_view_materials": can_view_materials,
        },
    )


@student_required
@require_POST
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
    )

    if enrollment.is_blocked:
        return redirect("course_detail", course_id=course.id)

    if created:
        Notification.objects.create(
            to_user=course.teacher,
            text=f"{request.user.username} enrolled in your course '{course.title}'",
            link=f"/courses/{course.id}/",
        )

    return redirect("course_detail", course_id=course.id)


@student_required
@require_POST
def submit_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Must be enrolled AND not blocked
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    if not enrollment or enrollment.is_blocked:
        raise PermissionDenied

    existing = Feedback.objects.filter(course=course, student=request.user).first()
    form = FeedbackForm(
        request.POST,
        instance=existing,
        student=request.user,
        course=course,
    )

    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.course = course
        feedback.student = request.user
        feedback.save()

        # Notify teacher
        Notification.objects.create(
            to_user=course.teacher,
            text=f"{request.user.username} left feedback on '{course.title}'",
            link=f"/courses/{course.id}/",
        )

    return redirect("course_detail", course_id=course.id)


@teacher_required
def teacher_course_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Only the owner teacher can view
    if course.teacher_id != request.user.id:
        raise PermissionDenied

    feedbacks = course.feedbacks.select_related("student").order_by("-created_at")
    avg_rating = feedbacks.aggregate(avg=Avg("rating"))["avg"]

    return render(
        request,
        "courses/teacher_course_feedback.html",
        {
            "course": course,
            "feedbacks": feedbacks,
            "avg_rating": avg_rating,
        },
    )


@teacher_required
def upload_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Only the owner teacher can upload
    if course.teacher_id != request.user.id:
        raise PermissionDenied

    if request.method == "POST":
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.uploaded_by = request.user
            material.save()

            # Notify enrolled students (not blocked)
            enrollments = course.enrollments.filter(is_blocked=False).select_related("student")
            for e in enrollments:
                Notification.objects.create(
                    to_user=e.student,
                    text=f"New material in '{course.title}': {material.title}",
                    link=f"/courses/{course.id}/",
                )

            return redirect("course_detail", course_id=course.id)
    else:
        form = CourseMaterialForm()

    return render(
        request,
        "courses/upload_material.html",
        {"course": course, "form": form},
    )

@teacher_required
def manage_enrollments(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Only owner teacher
    if course.teacher_id != request.user.id:
        raise PermissionDenied

    enrollments = course.enrollments.select_related("student").order_by("student__username")

    return render(
        request,
        "courses/manage_enrollments.html",
        {"course": course, "enrollments": enrollments},
    )


@teacher_required
@require_POST
def block_student(request, course_id, enrollment_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher_id != request.user.id:
        raise PermissionDenied

    enrollment = get_object_or_404(Enrollment, id=enrollment_id, course_id=course_id)
    enrollment.is_blocked = True
    enrollment.blocked_at = timezone.now()
    enrollment.save(update_fields=["is_blocked", "blocked_at"])

    Notification.objects.create(
        to_user=enrollment.student,
        text=f"You were blocked from '{course.title}'.",
        link=f"/courses/{course.id}/",
    )

    return redirect("manage_enrollments", course_id=course.id)


@teacher_required
@require_POST
def unblock_student(request, course_id, enrollment_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher_id != request.user.id:
        raise PermissionDenied

    enrollment = get_object_or_404(Enrollment, id=enrollment_id, course_id=course_id)
    enrollment.is_blocked = False
    enrollment.blocked_at = None
    enrollment.blocked_reason = ""
    enrollment.save(update_fields=["is_blocked", "blocked_at", "blocked_reason"])

    Notification.objects.create(
        to_user=enrollment.student,
        text=f"You were unblocked in '{course.title}'.",
        link=f"/courses/{course.id}/",
    )

    return redirect("manage_enrollments", course_id=course.id)


@teacher_required
@require_POST
def remove_student(request, course_id, enrollment_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher_id != request.user.id:
        raise PermissionDenied

    enrollment = get_object_or_404(Enrollment, id=enrollment_id, course_id=course_id)
    student = enrollment.student
    enrollment.delete()

    Notification.objects.create(
        to_user=student,
        text=f"You were removed from '{course.title}'.",
        link=f"/courses/{course.id}/",
    )

    return redirect("manage_enrollments", course_id=course.id)

@login_required
def download_material(request, course_id, material_id):
    course = get_object_or_404(Course, id=course_id)
    material = get_object_or_404(CourseMaterial, id=material_id, course=course)

    # Teacher owner can always download
    if request.user.is_teacher() and course.teacher_id == request.user.id:
        return FileResponse(
            material.file.open("rb"),
            as_attachment=True,
            filename=material.file.name.split("/")[-1],
        )

    # Students: must be enrolled and NOT blocked
    if request.user.is_student():
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
        if not enrollment or enrollment.is_blocked:
            raise PermissionDenied

        return FileResponse(
            material.file.open("rb"),
            as_attachment=True,
            filename=material.file.name.split("/")[-1],
        )

    raise PermissionDenied
