from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from courses.models import Course, Enrollment

User = get_user_model()


class BlockingTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="t1", password="pass")
        self.student = User.objects.create_user(username="s1", password="pass")

        # IMPORTANT: match your User.role TextChoices values
        self.teacher.role = User.Roles.TEACHER
        self.student.role = User.Roles.STUDENT
        self.teacher.save()
        self.student.save()

        self.course = Course.objects.create(teacher=self.teacher, title="C1", description="")
        self.enrollment = Enrollment.objects.create(course=self.course, student=self.student)

    def test_teacher_can_block_student(self):
        self.client.login(username="t1", password="pass")
        url = reverse("block_student", args=[self.course.id, self.enrollment.id])

        resp = self.client.post(url)
        self.assertIn(resp.status_code, (200, 302))

        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.is_blocked)

    def test_teacher_can_unblock_student(self):
        self.enrollment.is_blocked = True
        self.enrollment.save()

        self.client.login(username="t1", password="pass")
        url = reverse("unblock_student", args=[self.course.id, self.enrollment.id])

        resp = self.client.post(url)
        self.assertIn(resp.status_code, (200, 302))

        self.enrollment.refresh_from_db()
        self.assertFalse(self.enrollment.is_blocked)

    def test_teacher_can_remove_student(self):
        self.client.login(username="t1", password="pass")
        url = reverse("remove_student", args=[self.course.id, self.enrollment.id])

        resp = self.client.post(url)
        self.assertIn(resp.status_code, (200, 302))

        self.assertFalse(Enrollment.objects.filter(id=self.enrollment.id).exists())

    def test_student_cannot_block(self):
        self.client.login(username="s1", password="pass")
        url = reverse("block_student", args=[self.course.id, self.enrollment.id])

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)
