from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from courses.models import Course, Enrollment
from notifications.models import Notification

User = get_user_model()


class EnrollNotificationTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="t1", password="pass")
        self.student = User.objects.create_user(username="s1", password="pass")

        # IMPORTANT: match your User.role TextChoices values
        self.teacher.role = User.Roles.TEACHER
        self.student.role = User.Roles.STUDENT
        self.teacher.save()
        self.student.save()

        self.course = Course.objects.create(teacher=self.teacher, title="C1", description="")

    def test_student_enroll_creates_enrollment_and_notifies_teacher(self):
        self.client.login(username="s1", password="pass")

        url = reverse("enroll_course", args=[self.course.id])
        resp = self.client.post(url)
        self.assertIn(resp.status_code, (200, 302))

        self.assertTrue(Enrollment.objects.filter(course=self.course, student=self.student).exists())

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.teacher,
                text__icontains="enrolled",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )
