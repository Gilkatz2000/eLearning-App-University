import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from courses.models import Course, Enrollment


class CourseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = int(self.scope["url_route"]["kwargs"]["course_id"])
        self.room_group_name = f"course_chat_{self.course_id}"

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        allowed = await self.user_allowed_in_course(user_id=user.id, course_id=self.course_id)
        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "username": "system",
                "message": f"{user.username} joined the chat",
                "timestamp": timezone.now().isoformat(timespec="seconds"),
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]
        data = json.loads(text_data)
        message = (data.get("message") or "").strip()
        if not message:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "username": user.username,
                "message": message,
                "timestamp": timezone.now().isoformat(timespec="seconds"),
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "username": event["username"],
                    "message": event["message"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def user_allowed_in_course(self, user_id: int, course_id: int) -> bool:
        course = Course.objects.filter(id=course_id).select_related("teacher").first()
        if not course:
            return False

        if course.teacher_id == user_id:
            return True

        enrollment = Enrollment.objects.filter(course_id=course_id, student_id=user_id).first()
        if not enrollment:
            return False

        return not enrollment.is_blocked
