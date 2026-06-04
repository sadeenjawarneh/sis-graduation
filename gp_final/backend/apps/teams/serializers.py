from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team, ExamDate, MembershipRequest

User = get_user_model()


class ExamDateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ExamDate
        fields = ['id', 'date']


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'display_name', 'email', 'role']


class TeamSerializer(serializers.ModelSerializer):
    leader              = MemberSerializer(read_only=True)
    members             = MemberSerializer(many=True, read_only=True)
    members_info        = MemberSerializer(source='members', many=True, read_only=True)
    assigned_supervisor = MemberSerializer(read_only=True)
    exam_dates          = ExamDateSerializer(many=True, read_only=True)
    supervisor          = serializers.SerializerMethodField()
    members_count       = serializers.SerializerMethodField()

    def get_supervisor(self, obj):
        return obj.assigned_supervisor_id  # returns int or None

    def get_members_count(self, obj):
        return obj.members.count()

    class Meta:
        model  = Team
        fields = [
            'id', 'name', 'project_title', 'project_description',
            'status', 'leader', 'members', 'members_info', 'assigned_supervisor',
            'supervisor', 'members_count',
            'progress', 'academic_year', 'exam_dates',
            'created_at', 'updated_at',
        ]


class TeamCreateSerializer(serializers.ModelSerializer):
    project_title       = serializers.CharField(required=False, allow_blank=True, default='')
    project_description = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model  = Team
        fields = ['name', 'project_title', 'project_description', 'academic_year']

    def create(self, validated_data):
        user = self.context['request'].user
        # Default project_title to name if not provided
        if not validated_data.get('project_title'):
            validated_data['project_title'] = validated_data.get('name', '')
        # Accept 'description' as alias for 'project_description'
        team = Team.objects.create(leader=user, **validated_data)
        team.members.add(user)
        return team


class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Team
        fields = ['project_title', 'project_description', 'status', 'progress', 'academic_year']
        extra_kwargs = {f: {'required': False} for f in fields}


class ExamDateAddSerializer(serializers.Serializer):
    date = serializers.DateField()


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'display_name', 'email']

class MembershipRequestSerializer(serializers.ModelSerializer):
    student_info   = MemberSerializer(source='student', read_only=True)
    yes_count      = serializers.SerializerMethodField()
    no_count       = serializers.SerializerMethodField()
    my_vote        = serializers.SerializerMethodField()
    required_votes = serializers.SerializerMethodField()
    total_members  = serializers.SerializerMethodField()

    def get_yes_count(self, obj):
        return obj.yes_voters.count()

    def get_no_count(self, obj):
        return obj.no_voters.count()

    def get_my_vote(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if obj.yes_voters.filter(pk=request.user.pk).exists():
            return 'yes'
        if obj.no_voters.filter(pk=request.user.pk).exists():
            return 'no'
        return None

    def get_required_votes(self, obj):
        total = obj.team.members.count()
        return max(1, total // 2 + 1)   # strict majority

    def get_total_members(self, obj):
        return obj.team.members.count()

    class Meta:
        model  = MembershipRequest
        fields = [
            'id', 'team', 'student', 'student_info', 'status', 'created_at',
            'yes_count', 'no_count', 'my_vote', 'required_votes', 'total_members',
        ]
