from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer


# ── List notifications for current user ───────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    GET /api/v1/notifications/
    Optional query param: ?unread=true  → only unread notifications
    """
    qs = Notification.objects.filter(recipient=request.user)
    if request.query_params.get('unread', '').lower() == 'true':
        qs = qs.filter(is_read=False)
    return Response(NotificationSerializer(qs, many=True).data)


# ── Unread count ──────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """GET /api/v1/notifications/unread-count/"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'unread_count': count})


# ── Mark all as read ──────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """POST /api/v1/notifications/mark-all-read/"""
    updated = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    return Response({'marked_read': updated})


# ── Mark single notification as read ─────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_one_read(request, pk):
    """PATCH /api/v1/notifications/<pk>/read/"""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    return Response(NotificationSerializer(notif).data)


# ── Delete a notification ─────────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    """DELETE /api/v1/notifications/<pk>/"""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    return Response({'detail': 'Notification deleted.'}, status=204)
