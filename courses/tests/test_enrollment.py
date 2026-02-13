# courses/tests/test_enrollment.py

from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment
from notifications.models import Notification
from tests.helpers import make_teacher, make_student


class CourseEnrollmentFlowTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher(username="alice", password="pass")
        self.student = make_student(username="bob", password="pass")

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Intro to Django",
            description="Basics",
        )

    def test_student_can_enroll_in_course(self):
        self.client.login(username="bob", password="pass")

        response = self.client.post(reverse("enroll_course", args=[self.course.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Enrollment.objects.filter(course=self.course, student=self.student).exists()
        )

    def test_teacher_is_notified_when_student_enrolls(self):
        self.client.login(username="bob", password="pass")

        self.client.post(reverse("enroll_course", args=[self.course.id]))

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.teacher,
                text__icontains="enrolled",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )
