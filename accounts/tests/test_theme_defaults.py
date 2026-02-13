from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserThemeTests(TestCase):
    def test_theme_defaults_to_default(self):
        user = User.objects.create_user(username="bob", password="pass")
        self.assertEqual(user.theme, User.Themes.DEFAULT)
