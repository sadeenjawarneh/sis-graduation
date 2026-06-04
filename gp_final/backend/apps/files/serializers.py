# ── serializers.py ────────────────────────────────────────────────────────────
from rest_framework import serializers
from .models import TeamFile


class TeamFileSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='uploader.display_name', read_only=True)
    team_name     = serializers.CharField(source='team.name', read_only=True)
    file_url      = serializers.SerializerMethodField()

    class Meta:
        model  = TeamFile
        fields = ['id', 'team', 'team_name', 'uploader_name', 'file_url', 'file_name', 'description', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


