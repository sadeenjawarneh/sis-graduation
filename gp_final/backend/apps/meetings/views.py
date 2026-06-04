import datetime
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.teams.models import Team
from apps.notifications.utils import push_notification
from .models import AvailabilitySlot, Meeting
from .serializers import (
    AvailabilitySlotSerializer, AvailabilitySlotCreateSerializer,
    MeetingSerializer, BookMeetingSerializer,
)


# ─── helpers ─────────────────────────────────────────────────────────────────
def _to_minutes(t):
    return t.hour * 60 + t.minute


def _from_minutes(mins):
    return datetime.time(hour=mins // 60, minute=mins % 60)


def _generate_half_hour_slots(slot):
    """Yield datetime.time objects every 30 min inside an AvailabilitySlot."""
    start = _to_minutes(slot.start_time)
    end   = _to_minutes(slot.end_time)
    t = start
    while t + 30 <= end:
        yield _from_minutes(t)
        t += 30


def _slot_is_open(slot):
    dt = timezone.make_aware(datetime.datetime.combine(slot.date, slot.end_time))
    return dt >= timezone.now()


def _find_best_slot(supervisor, mode, exam_dates=None):
    """
    Find the earliest available 30-min sub-slot for the supervisor
    that matches the requested mode and has no existing booking conflict,
    and does not fall on a team exam date.
    Returns (date, time) or None.
    """
    exam_dates = exam_dates or set()
    slots = (
        AvailabilitySlot.objects
        .filter(supervisor=supervisor)
        .filter(mode__in=[mode, 'Both'])
        .order_by('date', 'start_time')
    )
    booked = set(
        Meeting.objects.filter(supervisor=supervisor)
        .values_list('date', 'time')
    )

    for slot in slots:
        if not _slot_is_open(slot):
            continue
        if slot.date in exam_dates:
            continue
        for t in _generate_half_hour_slots(slot):
            if (slot.date, t) not in booked:
                return slot.date, t
    return None


def _fairness_check(supervisor, team):
    """
    Ensure fair meeting distribution: a team must not have more than
    (min_count + 1) meetings compared to the supervisor's least-met team.
    Returns (ok: bool, error: str | None).
    """
    my_teams = Team.objects.filter(assigned_supervisor=supervisor)
    if my_teams.count() <= 1:
        return True, None

    counts = {
        t.pk: Meeting.objects.filter(supervisor=supervisor, team=t).count()
        for t in my_teams
    }
    team_count = counts.get(team.pk, 0)
    min_count  = min(counts.values())
    if team_count > min_count + 1:
        return False, 'Fair distribution: schedule a team with fewer meetings first.'
    return True, None


# ─── Availability Slots ───────────────────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def availability_slots(request):
    """
    GET  /api/v1/meetings/slots/   → supervisor's own slots
    POST /api/v1/meetings/slots/   → add a new slot
    """
    if request.user.role != UserRole.SUPERVISOR:
        return Response({'error': 'Only supervisors can manage availability slots.'}, status=403)

    if request.method == 'GET':
        slots = AvailabilitySlot.objects.filter(supervisor=request.user)
        return Response(AvailabilitySlotSerializer(slots, many=True).data)

    serializer = AvailabilitySlotCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    slot = serializer.save()
    return Response(AvailabilitySlotSerializer(slot).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_slot(request, pk):
    """DELETE /api/v1/meetings/slots/<pk>/"""
    slot = get_object_or_404(AvailabilitySlot, pk=pk, supervisor=request.user)
    slot.delete()
    return Response({'detail': 'Slot deleted.'}, status=204)


# ─── Book Meeting (auto-select best slot) ────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_meeting(request):
    """
    POST /api/v1/meetings/book/
    Body: { team_id, meeting_type: 'Direct'|'Online', topic }
    Supervisor only. Auto-selects earliest conflict-free slot.
    """
    if request.user.role != UserRole.SUPERVISOR:
        return Response({'error': 'Only supervisors can book meetings.'}, status=403)

    serializer = BookMeetingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    team = get_object_or_404(Team, pk=data['team_id'])

    if team.assigned_supervisor != request.user:
        return Response({'error': 'This team is not assigned to you.'}, status=403)

    # Exam-date conflict check
    exam_dates = set(team.exam_dates.values_list('date', flat=True))

    # Fairness check
    ok, err = _fairness_check(request.user, team)
    if not ok:
        return Response({'error': err}, status=400)

    # Find best slot (already skips exam dates)
    with transaction.atomic():
        result = _find_best_slot(request.user, data['meeting_type'], exam_dates)
        if result is None:
            return Response({'error': 'No available slot found. All slots may be on exam days or fully booked.'}, status=400)

        date, time = result

        meeting = Meeting.objects.create(
            supervisor=request.user,
            team=team,
            date=date,
            time=time,
            meeting_type=data['meeting_type'],
            topic=data['topic'],
        )

    # Update team next_meeting field (store as string for front-end parity)
    team.save()   # triggers auto_now on updated_at

    # Notify team members
    for member in team.members.all():
        push_notification(
            recipient_id=member.pk,
            title='Meeting scheduled',
            message=(
                f'Dr. {request.user.display_name} scheduled a {data["meeting_type"]} '
                f'meeting on {date} at {time.strftime("%H:%M")}. Topic: {data["topic"] or "—"}'
            ),
            notif_type='meeting_scheduled',
            team_name=team.name,
        )

    push_notification(
        recipient_id=request.user.pk,
        title='Meeting booked',
        message=f'Meeting with {team.name} booked on {date} at {time.strftime("%H:%M")}.',
        notif_type='meeting_booked',
        team_name=team.name,
    )

    return Response(MeetingSerializer(meeting).data, status=201)


# ─── List meetings ────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meeting_list(request):
    """
    GET /api/v1/meetings/
    Supervisor → their meetings.  Student → meetings of their teams.
    """
    user = request.user
    if user.role == UserRole.SUPERVISOR:
        meetings = Meeting.objects.filter(supervisor=user)
    elif user.role == UserRole.STUDENT:
        teams    = Team.objects.filter(members=user)
        meetings = Meeting.objects.filter(team__in=teams)
    else:
        meetings = Meeting.objects.all()

    return Response(MeetingSerializer(meetings, many=True).data)
