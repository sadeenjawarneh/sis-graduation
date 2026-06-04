from rest_framework import serializers
from .models import AvailabilitySlot, Meeting


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    is_open = serializers.ReadOnlyField()

    class Meta:
        model  = AvailabilitySlot
        fields = ['id', 'date', 'start_time', 'end_time', 'mode', 'is_open', 'created_at']


class AvailabilitySlotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time', 'mode']

    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError('end_time must be after start_time.')
        return data

    def create(self, validated_data):
        supervisor = self.context['request'].user
        return AvailabilitySlot.objects.create(supervisor=supervisor, **validated_data)


class MeetingSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.display_name', read_only=True)
    team_name       = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model  = Meeting
        fields = [
            'id', 'supervisor_name', 'team_name',
            'date', 'time', 'meeting_type', 'topic', 'created_at',
        ]


class BookMeetingSerializer(serializers.Serializer):
    team_id      = serializers.IntegerField()
    meeting_type = serializers.ChoiceField(choices=['Direct', 'Online'])
    topic        = serializers.CharField(max_length=500, allow_blank=True, default='')
