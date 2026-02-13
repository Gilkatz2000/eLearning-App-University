from django.contrib.auth import get_user_model

User = get_user_model()

def make_teacher(username="alice", password="pass"):
    user = User.objects.create_user(username=username, password=password)
    user.role = User.Roles.TEACHER
    user.save(update_fields=["role"])
    return user

def make_student(username="bob", password="pass"):
    user = User.objects.create_user(username=username, password=password)
    user.role = User.Roles.STUDENT
    user.save(update_fields=["role"])
    return user
