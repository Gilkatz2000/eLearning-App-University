from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from courses.models import Course, Enrollment, Feedback
from notifications.models import Notification
from tests.helpers import make_teacher, make_student

class CourseNotificationTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher("alice", "pass")
        self.student = make_student("bob", "pass")
        self.blocked_student = make_student("carl", "pass")

        self.course = Course.objects.create(teacher=self.teacher, title="Notify Me", description="x")

        Enrollment.objects.create(course=self.course, student=self.student, is_blocked=False)
        Enrollment.objects.create(course=self.course, student=self.blocked_student, is_blocked=True)

    def test_teacher_is_notified_when_student_leaves_feedback(self):
        self.client.login(username="bob", password="pass")

        resp = self.client.post(
            reverse("submit_feedback", args=[self.course.id]),
            data={"rating": "5", "comment": "Awesome"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Feedback.objects.filter(course=self.course, student=self.student).exists())

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.teacher,
                text__icontains="left feedback",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )

    def test_only_unblocked_enrolled_students_get_material_notification(self):
        self.client.login(username="alice", password="pass")

        fake_file = SimpleUploadedFile(
            "week1.pdf",
            b"%PDF-1.4 fake content",
            content_type="application/pdf",
        )

        resp = self.client.post(
            reverse("upload_material", args=[self.course.id]),
            data={"title": "Week 1", "file": fake_file},
        )
        self.assertEqual(resp.status_code, 302)

        # Unblocked student gets notified
        self.assertTrue(
            Notification.objects.filter(
                to_user=self.student,
                text__icontains="New material",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )

        # Blocked student should NOT get notified
        self.assertFalse(
            Notification.objects.filter(
                to_user=self.blocked_student,
                text__icontains="New material",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )
