from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from courses.models import Course, Enrollment

@login_required
def course_chat_room(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Superuser can view any course chat
    if request.user.is_staff or request.user.is_superuser:
        return render(request, "chat/course_chat_room.html", {"course": course})

    # Teacher owner can view
    if course.teacher_id == request.user.id:
        return render(request, "chat/course_chat_room.html", {"course": course})

    # Student must be enrolled and not blocked
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    if not enrollment or enrollment.is_blocked:
        raise PermissionDenied

    return render(request, "chat/course_chat_room.html", {"course": course})
