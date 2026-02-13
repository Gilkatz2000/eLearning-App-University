# courses/tests/test_feedback.py

from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment, Feedback
from tests.helpers import make_teacher, make_student


class CourseFeedbackTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher(username="alice", password="pass")
        self.student = make_student(username="bob", password="pass")

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Python Fundamentals",
            description="Core concepts",
        )

    def test_student_cannot_leave_feedback_without_enrolling(self):
        self.client.login(username="bob", password="pass")

        response = self.client.post(
            reverse("submit_feedback", args=[self.course.id]),
            data={"rating": "5", "comment": "Great course"},
        )

        self.assertEqual(response.status_code, 403)

    def test_enrolled_student_can_leave_feedback(self):
        Enrollment.objects.create(course=self.course, student=self.student, is_blocked=False)

        self.client.login(username="bob", password="pass")

        response = self.client.post(
            reverse("submit_feedback", args=[self.course.id]),
            data={"rating": "5", "comment": "Really helpful"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Feedback.objects.filter(course=self.course, student=self.student).exists()
        )

    def test_blocked_student_cannot_leave_feedback(self):
        Enrollment.objects.create(course=self.course, student=self.student, is_blocked=True)

        self.client.login(username="bob", password="pass")

        response = self.client.post(
            reverse("submit_feedback", args=[self.course.id]),
            data={"rating": "5", "comment": "Test"},
        )

        self.assertEqual(response.status_code, 403)
