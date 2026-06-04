from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SupervisorRequest

User = get_user_model()


class SupervisorRequestCreateSerializer(serializers.Serializer):
    team_id      = serializers.IntegerField()
    project_idea = serializers.CharField(max_length=500)
    preferences  = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=5,
    )


class SupervisorRequestSerializer(serializers.ModelSerializer):
    team_name          = serializers.CharField(source='team.name', read_only=True)
    leader_name        = serializers.CharField(source='leader.display_name', read_only=True)
    target_supervisor_name = serializers.CharField(
        source='target_supervisor.display_name', read_only=True, default=None
    )

    class Meta:
        model  = SupervisorRequest
        fields = [
            'id', 'team_name', 'leader_name', 'project_idea',
            'preferences', 'current_index',
            'target_supervisor_name', 'status',
            'decided_at', 'created_at',
        ]


class DecideRequestSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approve', 'reject'])
