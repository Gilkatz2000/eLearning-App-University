from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from accounts.models import StatusUpdate
from tests.helpers import make_teacher, make_student


class StatusUpdatesTests(APITestCase):
    def setUp(self):
        self.teacher = make_teacher("alice", "pass")
        self.student = make_student("bob", "pass")
        self.other_student = make_student("carl", "pass")

    def test_my_status_updates_requires_auth(self):
        url = reverse("api_my_status_updates")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_student_can_list_their_own_status_updates(self):
        StatusUpdate.objects.create(user=self.student, text="Hello")
        StatusUpdate.objects.create(user=self.student, text="Second")

        self.client.login(username="bob", password="pass")

        url = reverse("api_my_status_updates")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) >= 2)

    def test_student_can_create_status_update(self):
        self.client.login(username="bob", password="pass")

        url = reverse("api_my_status_updates")
        resp = self.client.post(url, data={"text": "New status"}, format="json")

        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertTrue(StatusUpdate.objects.filter(user=self.student, text="New status").exists())

    def test_rejects_empty_status_text(self):
        self.client.login(username="bob", password="pass")

        url = reverse("api_my_status_updates")
        resp = self.client.post(url, data={"text": ""}, format="json")

        self.assertIn(resp.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY))

    def test_rejects_too_long_status_text(self):
        self.client.login(username="bob", password="pass")

        url = reverse("api_my_status_updates")
        resp = self.client.post(url, data={"text": "x" * 501}, format="json")

        self.assertIn(resp.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY))

    def test_student_cannot_view_other_users_status_updates(self):
        StatusUpdate.objects.create(user=self.other_student, text="Private")

        self.client.login(username="bob", password="pass")

        url = reverse("api_user_status_updates", kwargs={"username": "carl"})
        resp = self.client.get(url)

        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_teacher_can_view_other_users_status_updates(self):
        StatusUpdate.objects.create(user=self.other_student, text="Visible to teacher")

        self.client.login(username="alice", password="pass")

        url = reverse("api_user_status_updates", kwargs={"username": "carl"})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item.get("text") == "Visible to teacher" for item in resp.data))
