# courses/tests/test_materials.py

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from courses.models import Course, Enrollment
from notifications.models import Notification
from tests.helpers import make_teacher, make_student


class CourseMaterialUploadTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher(username="alice", password="pass")
        self.student = make_student(username="bob", password="pass")

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Web Development",
            description="HTML & CSS",
        )

        Enrollment.objects.create(course=self.course, student=self.student, is_blocked=False)

    def test_uploading_material_notifies_enrolled_students(self):
        self.client.login(username="alice", password="pass")

        # Must use allowed extension after validators update
        fake_file = SimpleUploadedFile(
            "week1.pdf",
            b"%PDF-1.4 fake content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("upload_material", args=[self.course.id]),
            data={"title": "Week 1 Slides", "file": fake_file},
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.student,
                text__icontains="New material",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )
