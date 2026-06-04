import os
import uuid
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from apps.teams.models import Team
from .models import Message
from .serializers import MessageSerializer


class MessageHistoryView(generics.ListAPIView):
    """GET /api/chat/<team_id>/messages/?limit=50"""
    permission_classes = [IsAuthenticated]
    serializer_class   = MessageSerializer

    def get_queryset(self):
        team = get_object_or_404(Team, pk=self.kwargs['team_id'])
        is_member = team.members.filter(pk=self.request.user.pk).exists()
        is_supervisor = team.assigned_supervisor_id == self.request.user.pk
        if not (is_member or is_supervisor):
            return Message.objects.none()
        limit = int(self.request.query_params.get('limit', 50))
        return Message.objects.filter(
            team=team, deleted=False
        ).select_related('sender').order_by('-created_at')[:limit]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_chat_file(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    is_member = team.members.filter(pk=request.user.pk).exists()
    is_supervisor = getattr(team, 'assigned_supervisor_id', None) == request.user.pk
    if not (is_member or is_supervisor):
        return Response({'error': 'Not a team member.'}, status=403)

    file = request.FILES.get('file') or request.FILES.get('voice_note')
    if not file:
        return Response({'error': 'No file provided.'}, status=400)

    ext = os.path.splitext(file.name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'chat_files')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)
    with open(file_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)

    file_url = f'{settings.MEDIA_URL}chat_files/{unique_name}'
    return Response({'file_url': file_url})
