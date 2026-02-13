from django.urls import path
from .views import (
    MeAPIView,
    UserByUsernameAPIView,
    MyStatusUpdatesAPIView,
    UserStatusUpdatesAPIView,
)

urlpatterns = [
    path("me/", MeAPIView.as_view(), name="api_me"),
    path("users/<str:username>/", UserByUsernameAPIView.as_view(), name="api_user_by_username"),
    path("me/status-updates/", MyStatusUpdatesAPIView.as_view(), name="api_my_status_updates"),
    path("users/<str:username>/status-updates/", UserStatusUpdatesAPIView.as_view(), name="api_user_status_updates"),
]
