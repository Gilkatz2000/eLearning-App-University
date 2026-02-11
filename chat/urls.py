from django.urls import path
from . import views

urlpatterns = [
    path("courses/<int:course_id>/chat/", views.course_chat_room, name="course_chat_room"),
]
