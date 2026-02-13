from django.test import TestCase
from django.contrib.auth import get_user_model

from notifications.models import Notification

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass")

    def test_can_create_notification(self):
        n = Notification.objects.create(
            to_user=self.user,
            text="Hello from the system",
            link="/courses/1/",
        )
        self.assertEqual(n.to_user, self.user)
        self.assertIn("Hello", n.text)
        self.assertIn("/courses/1/", n.link)

    def test_notifications_can_be_sorted_newest_first(self):
        n1 = Notification.objects.create(
            to_user=self.user, text="Older", link="/a/"
        )
        n2 = Notification.objects.create(
            to_user=self.user, text="Newer", link="/b/"
        )

        qs = Notification.objects.filter(to_user=self.user).order_by("-id")
        self.assertEqual(qs.first().id, n2.id)
