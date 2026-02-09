from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("users/<str:username>/", views.user_home, name="user_home"),
    path("status/post/", views.post_status_update, name="post_status_update"),
]
