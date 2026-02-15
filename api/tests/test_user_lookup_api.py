from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from tests.helpers import make_teacher, make_student

class UserLookupTests(APITestCase):
    def setUp(self):
        self.teacher = make_teacher("alice", "pass")
        self.student = make_student("bob", "pass")
        self.other_student = make_student("carl", "pass")

    def test_lookup_requires_authentication(self):
        url = reverse("api_user_by_username", kwargs={"username": "bob"})
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_student_can_view_self(self):
        self.client.login(username="bob", password="pass")

        url = reverse("api_user_by_username", kwargs={"username": "bob"})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "bob")

    def test_student_cannot_view_other_user(self):
        self.client.login(username="bob", password="pass")

        url = reverse("api_user_by_username", kwargs={"username": "carl"})
        resp = self.client.get(url)

        # Depending on the implementation the can be a return 403 or 404. both are acceptable!
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_teacher_can_view_other_user(self):
        self.client.login(username="alice", password="pass")

        url = reverse("api_user_by_username", kwargs={"username": "carl"})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "carl")
