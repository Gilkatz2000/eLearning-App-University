from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def notifications_list(request):
    notifications = request.user.notifications.order_by("-created_at")
    return render(request, "notifications/list.html", {"notifications": notifications})
