import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator

from config.asgi import application
from courses.models import Course, Enrollment
from tests.helpers import make_teacher, make_student

@sync_to_async
def _setup_course_with_enrollment(blocked: bool | None):
    teacher = make_teacher("alice", "pass")
    student = make_student("bob", "pass")
    course = Course.objects.create(teacher=teacher, title="Chat Course", description="x")

    if blocked is not None:
        Enrollment.objects.create(course=course, student=student, is_blocked=blocked)

    return student, course


def _ws_path(course_id: int) -> str:
    # matches chat/routing.py: r"ws/courses/(?P<course_id>\d+)/chat/$"
    return f"/ws/courses/{course_id}/chat/"

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_enrolled_student_can_connect_to_course_chat():
    student, course = await _setup_course_with_enrollment(blocked=False)

    communicator = WebsocketCommunicator(application, _ws_path(course.id))
    communicator.scope["user"] = student

    connected, _ = await communicator.connect()
    try:
        assert connected is True
    finally:
        await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_blocked_student_cannot_connect_to_course_chat():
    student, course = await _setup_course_with_enrollment(blocked=True)

    communicator = WebsocketCommunicator(application, _ws_path(course.id))
    communicator.scope["user"] = student

    try:
        connected, _ = await communicator.connect()
        assert connected is False
    finally:
        await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_not_enrolled_student_cannot_connect_to_course_chat():
    student, course = await _setup_course_with_enrollment(blocked=None)

    communicator = WebsocketCommunicator(application, _ws_path(course.id))
    communicator.scope["user"] = student

    try:
        connected, _ = await communicator.connect()
        assert connected is False
    finally:
        await communicator.disconnect()
