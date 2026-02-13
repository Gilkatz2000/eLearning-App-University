# api/serializers.py

from rest_framework import serializers
from accounts.models import User, StatusUpdate


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "photo"]


class StatusUpdateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = StatusUpdate
        fields = ["id", "user", "text", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate_text(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Status update cannot be empty.")
        if len(v) > 280:
            raise serializers.ValidationError("Status update too long (max 280 characters).")
        return v
