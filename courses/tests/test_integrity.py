from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment, Feedback
from tests.helpers import make_teacher, make_student


class CourseIntegrityTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher("alice", "pass")
        self.student = make_student("bob", "pass")
        self.course = Course.objects.create(teacher=self.teacher, title="Integrity 101", description="x")

    def test_enrollment_is_unique_per_student_per_course(self):
        self.client.login(username="bob", password="pass")

        resp1 = self.client.post(reverse("enroll_course", args=[self.course.id]))
        self.assertEqual(resp1.status_code, 302)

        resp2 = self.client.post(reverse("enroll_course", args=[self.course.id]))
        self.assertEqual(resp2.status_code, 302)

        self.assertEqual(
            Enrollment.objects.filter(course=self.course, student=self.student).count(),
            1
        )

    def test_feedback_is_single_record_and_updates_on_resubmit(self):
        Enrollment.objects.create(course=self.course, student=self.student, is_blocked=False)

        self.client.login(username="bob", password="pass")

        resp1 = self.client.post(
            reverse("submit_feedback", args=[self.course.id]),
            data={"rating": "5", "comment": "Great"},
        )
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(
            Feedback.objects.filter(course=self.course, student=self.student).count(),
            1
        )

        resp2 = self.client.post(
            reverse("submit_feedback", args=[self.course.id]),
            data={"rating": "2", "comment": "Changed my mind"},
        )
        self.assertEqual(resp2.status_code, 302)

        self.assertEqual(
            Feedback.objects.filter(course=self.course, student=self.student).count(),
            1
        )
        fb = Feedback.objects.get(course=self.course, student=self.student)
        self.assertEqual(fb.rating, 2)
        self.assertIn("Changed", fb.comment)
