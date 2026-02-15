from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from tests.helpers import make_teacher, make_student

class MeEndpointTests(APITestCase):
    def setUp(self):
        self.student = make_student("bob", "pass")

    def test_me_requires_authentication(self):
        url = reverse("api_me")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_me_returns_current_user(self):
        self.client.login(username="bob", password="pass")

        url = reverse("api_me")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "bob")
