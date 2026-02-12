from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from courses.models import Course, Enrollment
from notifications.models import Notification

User = get_user_model()


class MaterialNotificationTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="t1", password="pass")
        self.student = User.objects.create_user(username="s1", password="pass")

        # IMPORTANT: match your User.role TextChoices values
        self.teacher.role = User.Roles.TEACHER
        self.student.role = User.Roles.STUDENT
        self.teacher.save()
        self.student.save()

        self.course = Course.objects.create(teacher=self.teacher, title="C1", description="")
        Enrollment.objects.create(course=self.course, student=self.student)

    def test_upload_material_notifies_enrolled_students(self):
        self.client.login(username="t1", password="pass")
        url = reverse("upload_material", args=[self.course.id])

        fake_file = SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")

        # NOTE: this assumes CourseMaterialForm fields are: title + file
        resp = self.client.post(url, data={"title": "Week 1", "file": fake_file})
        self.assertIn(resp.status_code, (200, 302))

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.student,
                text__icontains="New material",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )
