import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_chat_file(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if not team.members.filter(pk=request.user.pk).exists():
        return Response({'error': 'Not a team member.'}, status=403)
    
    file = request.FILES.get('file') or request.FILES.get('voice_note')
    if not file:
        return Response({'error': 'No file provided.'}, status=400)
    
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'chat_files')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.name)
    with open(file_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    
    file_url = f'{settings.MEDIA_URL}chat_files/{file.name}'
    return Response({'file_url': file_url})