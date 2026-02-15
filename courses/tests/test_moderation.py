from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment
from notifications.models import Notification
from tests.helpers import make_teacher, make_student

class CourseModerationTests(TestCase):
    def setUp(self):
        self.owner_teacher = make_teacher("alice", "pass")
        self.other_teacher = make_teacher("eve", "pass")
        self.student = make_student("bob", "pass")

        self.course = Course.objects.create(
            teacher=self.owner_teacher,
            title="Intro to Moderation",
            description="x",
        )

        self.enrollment = Enrollment.objects.create(
            course=self.course,
            student=self.student,
            is_blocked=False,
        )

    def test_owner_teacher_can_block_student(self):
        self.client.login(username="alice", password="pass")

        resp = self.client.post(
            reverse("block_student", args=[self.course.id, self.enrollment.id])
        )
        self.assertEqual(resp.status_code, 302)

        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.is_blocked)

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.student,
                text__icontains="blocked",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )

    def test_owner_teacher_can_unblock_student(self):
        self.enrollment.is_blocked = True
        self.enrollment.save(update_fields=["is_blocked"])

        self.client.login(username="alice", password="pass")

        resp = self.client.post(
            reverse("unblock_student", args=[self.course.id, self.enrollment.id])
        )
        self.assertEqual(resp.status_code, 302)

        self.enrollment.refresh_from_db()
        self.assertFalse(self.enrollment.is_blocked)

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.student,
                text__icontains="unblocked",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )

    def test_owner_teacher_can_remove_student(self):
        self.client.login(username="alice", password="pass")

        resp = self.client.post(
            reverse("remove_student", args=[self.course.id, self.enrollment.id])
        )
        self.assertEqual(resp.status_code, 302)

        self.assertFalse(
            Enrollment.objects.filter(id=self.enrollment.id).exists()
        )

        self.assertTrue(
            Notification.objects.filter(
                to_user=self.student,
                text__icontains="removed",
                link__contains=f"/courses/{self.course.id}/",
            ).exists()
        )

    def test_non_owner_teacher_cannot_moderate_course(self):
        self.client.login(username="eve", password="pass")

        resp_block = self.client.post(
            reverse("block_student", args=[self.course.id, self.enrollment.id])
        )
        self.assertEqual(resp_block.status_code, 403)

        resp_unblock = self.client.post(
            reverse("unblock_student", args=[self.course.id, self.enrollment.id])
        )
        self.assertEqual(resp_unblock.status_code, 403)

        resp_remove = self.client.post(
            reverse("remove_student", args=[self.course.id, self.enrollment.id])
        )
        self.assertEqual(resp_remove.status_code, 403)
