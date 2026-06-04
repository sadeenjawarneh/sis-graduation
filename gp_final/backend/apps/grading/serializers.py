from rest_framework import serializers
from django.conf import settings
from .models import GradingReport


class GradingReportSerializer(serializers.ModelSerializer):
    team_name       = serializers.CharField(source='team.name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.display_name', read_only=True)
    archived_file_url = serializers.SerializerMethodField()

    class Meta:
        model  = GradingReport
        fields = [
            'id', 'team_name', 'supervisor_name', 'phase',
            'chief_grade', 'examiner_one_grade', 'examiner_two_grade',
            'final_grade', 'feedback', 'archived_file_url', 'created_at',
        ]

    def get_archived_file_url(self, obj):
        request = self.context.get('request')
        if obj.archived_file and request:
            return request.build_absolute_uri(obj.archived_file.url)
        return None


class GradingReportCreateSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField(write_only=True)

    class Meta:
        model  = GradingReport
        fields = [
            'team_id', 'phase',
            'chief_grade', 'examiner_one_grade', 'examiner_two_grade',
            'feedback', 'archived_file',
        ]
        extra_kwargs = {'archived_file': {'required': False}}

    def validate(self, data):
        for field in ('chief_grade', 'examiner_one_grade', 'examiner_two_grade'):
            val = float(data.get(field, 0))
            if not (0 <= val <= 100):
                raise serializers.ValidationError({field: 'Grade must be between 0 and 100.'})
        return data


class GradePreviewSerializer(serializers.Serializer):
    """Compute a live preview of the weighted final grade without saving."""
    from decimal import Decimal as D
    chief_grade        = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=D('0'), max_value=D('100'))
    examiner_one_grade = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=D('0'), max_value=D('100'))
    examiner_two_grade = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=D('0'), max_value=D('100'))
