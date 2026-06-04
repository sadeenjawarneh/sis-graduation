from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.teams.models import Team
from apps.notifications.utils import push_notification
from .models import GradingReport
from .serializers import (
    GradingReportSerializer, GradingReportCreateSerializer, GradePreviewSerializer
)


# ── Preview (no save) ─────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_preview(request):
    """
    POST /api/v1/grading/preview/
    Body: { chief_grade, examiner_one_grade, examiner_two_grade }
    Returns computed final_grade using the 50/25/25 formula.
    """
    serializer = GradePreviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    weights = getattr(settings, 'GRADING_WEIGHTS', {
        'chief_supervisor': 0.50,
        'examiner_one':     0.25,
        'examiner_two':     0.25,
    })
    final = (
        float(d['chief_grade'])        * weights['chief_supervisor'] +
        float(d['examiner_one_grade']) * weights['examiner_one'] +
        float(d['examiner_two_grade']) * weights['examiner_two']
    )
    return Response({'final_grade': round(final, 2)})


# ── Create report ─────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    """
    POST /api/v1/grading/
    Multipart form (supports file upload):
      team_id, phase, chief_grade, examiner_one_grade, examiner_two_grade, feedback, archived_file
    Supervisor only; team must be assigned to them.
    """
    if request.user.role != 'supervisor':
        return Response({'error': 'Only supervisors can submit grading reports.'}, status=403)

    serializer = GradingReportCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    team = get_object_or_404(Team, pk=data.pop('team_id'))
    if team.assigned_supervisor != request.user:
        return Response({'error': 'This team is not assigned to you.'}, status=403)

    report = GradingReport.objects.create(team=team, supervisor=request.user, **data)

    # Notify every team member
    for member in team.members.all():
        push_notification(
            recipient_id=member.pk,
            title='Grade published',
            message=(
                f'Your {report.phase} grade has been published. '
                f'Final: {report.final_grade}/100.'
            ),
            notif_type='grade_published',
            team_name=team.name,
        )

    push_notification(
        recipient_id=request.user.pk,
        title='Report archived',
        message=f'Report for {team.name} ({report.phase}) saved successfully.',
        notif_type='report_saved',
        team_name=team.name,
    )

    return Response(
        GradingReportSerializer(report, context={'request': request}).data,
        status=201,
    )


# ── List reports ──────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reports(request):
    """
    GET /api/v1/grading/
    Optional query params: ?team=<name>&phase=<Proposal|Midterm|Final>
    """
    user = request.user
    if user.role == 'supervisor':
        qs = GradingReport.objects.filter(supervisor=user)
    elif user.role == 'student':
        teams = Team.objects.filter(members=user)
        qs    = GradingReport.objects.filter(team__in=teams)
    else:
        qs = GradingReport.objects.all()

    team_q  = request.query_params.get('team')
    phase_q = request.query_params.get('phase')
    if team_q:
        qs = qs.filter(team__name__icontains=team_q)
    if phase_q:
        qs = qs.filter(phase=phase_q)

    return Response(GradingReportSerializer(qs, many=True, context={'request': request}).data)
