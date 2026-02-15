from django.conf import settings
from django.db import models

class Notification(models.Model):
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Notif(to={self.to_user.username}, read={self.is_read})"
