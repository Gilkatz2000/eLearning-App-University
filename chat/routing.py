from django.urls import re_path
from .consumers import CourseChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/courses/(?P<course_id>\d+)/chat/$", CourseChatConsumer.as_asgi()),
]
