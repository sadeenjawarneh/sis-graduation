from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_info = UserSerializer(source='sender', read_only=True)

    class Meta:
        model  = Message
        fields = ['id', 'team', 'sender', 'sender_info', 'text', 'deleted', 'edited', 'created_at']
        read_only_fields = ['id', 'sender', 'deleted', 'edited', 'created_at']
