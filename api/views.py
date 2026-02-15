from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User, StatusUpdate
from .serializers import UserPublicSerializer, StatusUpdateSerializer

class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)

class UserByUsernameAPIView(APIView):
    # Teacher can view any user.
    # Students can view only themselves. 
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        target = get_object_or_404(User, username=username)

        if request.user.is_teacher():
            return Response(UserPublicSerializer(target).data)

        if request.user.username != username:
            raise PermissionDenied("Forbidden")

        return Response(UserPublicSerializer(target).data)

class MyStatusUpdatesAPIView(ListCreateAPIView):
    # GET: list my status updates
    # POST: create a new status update (students only)

    serializer_class = StatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StatusUpdate.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        if not self.request.user.is_student():
            # Teachers cannot post status updates
            raise PermissionDenied("Only students can post status updates.")
        serializer.save(user=self.request.user)

class UserStatusUpdatesAPIView(ListAPIView):
    # Teacher can view any user's updates.
    # Students can view only their own.
    serializer_class = StatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs["username"]
        target = get_object_or_404(User, username=username)

        if self.request.user.is_teacher():
            return StatusUpdate.objects.filter(user=target).order_by("-created_at")

        if self.request.user.username != username:
            raise PermissionDenied("Forbidden")

        return StatusUpdate.objects.filter(user=target).order_by("-created_at")
