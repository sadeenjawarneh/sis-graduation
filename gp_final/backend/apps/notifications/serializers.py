from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = [
            'id', 'title', 'message', 'notif_type',
            'team_name', 'is_read', 'created_at',
        ]
