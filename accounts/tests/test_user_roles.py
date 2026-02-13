from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRoleTests(TestCase):
    def test_new_user_defaults_to_student_role(self):
        user = User.objects.create_user(username="bob", password="pass")
        self.assertEqual(user.role, User.Roles.STUDENT)
        self.assertTrue(user.is_student())
        self.assertFalse(user.is_teacher())

    def test_teacher_role_method(self):
        user = User.objects.create_user(username="alice", password="pass")
        user.role = User.Roles.TEACHER
        user.save(update_fields=["role"])

        self.assertTrue(user.is_teacher())
        self.assertFalse(user.is_student())

    def test_student_role_method(self):
        user = User.objects.create_user(username="carl", password="pass")
        user.role = User.Roles.STUDENT
        user.save(update_fields=["role"])

        self.assertTrue(user.is_student())
        self.assertFalse(user.is_teacher())
