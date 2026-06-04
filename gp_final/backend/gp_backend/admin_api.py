"""
Admin-only API views — aggregate data from multiple apps for the admin panel.
All endpoints require the requesting user to have role='admin'.
"""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()


def _admin_only(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin only.'}, status=403)
    return None


def _letter(g):
    g = float(g)
    if g >= 97: return 'A+'
    if g >= 93: return 'A'
    if g >= 90: return 'A-'
    if g >= 87: return 'B+'
    if g >= 83: return 'B'
    if g >= 80: return 'B-'
    if g >= 77: return 'C+'
    if g >= 73: return 'C'
    if g >= 70: return 'C-'
    if g >= 67: return 'D+'
    if g >= 60: return 'D'
    return 'F'


# ── Dashboard ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    guard = _admin_only(request)
    if guard: return guard
    from apps.teams.models import Team
    from apps.requests.models import SupervisorRequest
    from apps.grading.models import GradingReport
    from apps.meetings.models import Meeting
    today = timezone.now().date()
    return Response({
        'success': True,
        'teams':       Team.objects.count(),
        'students':    User.objects.filter(role='student', is_active=True).count(),
        'supervisors': User.objects.filter(role='supervisor', is_active=True).count(),
        'proposals':   SupervisorRequest.objects.count(),
        'meetings':    Meeting.objects.filter(date__gte=today).count(),
    })


# ── Proposals (mapped to SupervisorRequests) ──────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def proposals_list(request):
    guard = _admin_only(request)
    if guard: return guard
    from apps.requests.models import SupervisorRequest

    if request.method == 'POST':
        return Response({'success': False, 'message': 'Proposals are submitted by students.'}, status=400)

    qs = SupervisorRequest.objects.select_related('team', 'leader', 'target_supervisor').order_by('-created_at')
    proposals = [{
        'id':           r.id,
        'team_name':    r.team.name if r.team else '—',
        'team_id':      r.team_id,
        'title':        r.project_idea or '—',
        'supervisor': {
            'id':   r.target_supervisor_id,
            'name': r.target_supervisor.display_name if r.target_supervisor else '—',
        },
        'submitted_at': r.created_at.isoformat() if r.created_at else None,
        'status':       r.status,
        'file_name':    None,
        'file_url':     None,
    } for r in qs]
    return Response({'success': True, 'proposals': proposals})


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def proposal_detail(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    from apps.requests.models import SupervisorRequest
    req = get_object_or_404(SupervisorRequest, pk=pk)
    if request.method == 'DELETE':
        req.delete()
        return Response({'success': True, 'message': 'Proposal deleted.'})
    if request.method == 'PUT':
        req.project_idea = request.data.get('title', req.project_idea)
        req.save(update_fields=['project_idea'])
        return Response({'success': True, 'message': 'Proposal updated.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def proposal_approve(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    from apps.requests.models import SupervisorRequest
    req = get_object_or_404(SupervisorRequest, pk=pk)
    req.status = 'approved'
    req.decided_at = timezone.now()
    req.save(update_fields=['status', 'decided_at'])
    if req.team and req.target_supervisor:
        req.team.assigned_supervisor = req.target_supervisor
        req.team.status = 'active'
        req.team.save(update_fields=['assigned_supervisor', 'status'])
    return Response({'success': True, 'message': 'Proposal approved and supervisor assigned.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def proposal_reject(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    from apps.requests.models import SupervisorRequest
    req = get_object_or_404(SupervisorRequest, pk=pk)
    req.status = 'rejected'
    req.decided_at = timezone.now()
    req.save(update_fields=['status', 'decided_at'])
    return Response({'success': True, 'message': 'Proposal rejected.'})


# ── Defense Schedule (mapped to Meetings) ─────────────────────────────────────

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def defense_detail(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    from apps.meetings.models import Meeting
    m = get_object_or_404(Meeting, pk=pk)

    if request.method == 'DELETE':
        m.delete()
        return Response({'success': True, 'message': 'Defense session deleted.'})

    if request.method == 'PUT':
        if 'date' in request.data:
            m.date = request.data['date']
        if 'time' in request.data:
            m.time = request.data['time']
        if 'location' in request.data:
            m.topic = f'Defense — {request.data["location"]}'
        m.save()
        return Response({'success': True, 'message': 'Defense session updated.'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def defense_list(request):
    guard = _admin_only(request)
    if guard: return guard
    from apps.meetings.models import Meeting
    from apps.teams.models import Team

    if request.method == 'POST':
        team_id  = request.data.get('team_id')
        date     = request.data.get('date')
        time_val = request.data.get('time', '10:00')
        location = request.data.get('location', 'Main Hall')
        if not team_id or not date:
            return Response({'error': 'team_id and date are required.'}, status=400)
        team = get_object_or_404(Team, pk=team_id)
        supervisor = team.assigned_supervisor
        if not supervisor:
            return Response({'error': 'Team has no assigned supervisor.'}, status=400)
        m = Meeting.objects.create(
            team=team, supervisor=supervisor,
            date=date, time=time_val,
            meeting_type='Direct',
            topic=f'Defense — {location}',
        )
        return Response({'success': True, 'message': 'Defense session scheduled.', 'data': {
            'id': m.id, 'team_name': team.name, 'date': str(m.date), 'time': str(m.time), 'location': location,
        }})

    meetings = Meeting.objects.select_related('team', 'supervisor').order_by('date', 'time')
    defenses = [{
        'id':       m.id,
        'team_id':  m.team_id,
        'team_name': m.team.name if m.team else '—',
        'date':     str(m.date),
        'time':     str(m.time),
        'location': m.topic.replace('Defense — ', '') if m.topic and 'Defense' in m.topic else (m.topic or 'TBD'),
        'supervisor': m.supervisor.display_name if m.supervisor else '—',
    } for m in meetings]
    return Response({'success': True, 'defenses': defenses})


# ── Grades ─────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grades_list(request):
    guard = _admin_only(request)
    if guard: return guard
    from apps.grading.models import GradingReport
    qs = GradingReport.objects.select_related('team', 'supervisor').order_by('-created_at')
    grades = [{
        'id':               g.id,
        'team_id':          g.team_id,
        'team_name':        g.team.name if g.team else '—',
        'project_title':    g.team.project_title if g.team else '—',
        'supervisor_name':  g.supervisor.display_name if g.supervisor else '—',
        'supervisor_grade': float(g.chief_grade),
        'committee1_grade': float(g.examiner_one_grade),
        'committee2_grade': float(g.examiner_two_grade),
        'final_grade':      float(g.final_grade),
        'letter_grade':     _letter(g.final_grade),
        'status':           'submitted',
        'phase':            g.phase,
    } for g in qs]
    return Response({'success': True, 'grades': grades})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grades_create(request):
    guard = _admin_only(request)
    if guard: return guard
    from apps.grading.models import GradingReport
    from apps.teams.models import Team
    team_id = request.data.get('team_id')
    if not team_id:
        return Response({'error': 'team_id is required.'}, status=400)
    team = get_object_or_404(Team, pk=team_id)
    supervisor = team.assigned_supervisor
    try:
        g, _ = GradingReport.objects.update_or_create(
            team=team, phase='Final',
            defaults={
                'supervisor':         supervisor,
                'chief_grade':        float(request.data.get('supervisor_grade', 0)),
                'examiner_one_grade': float(request.data.get('committee1_grade', 0)),
                'examiner_two_grade': float(request.data.get('committee2_grade', 0)),
            }
        )
        return Response({'success': True, 'message': 'Grade saved successfully.'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_approve(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    return Response({'success': True, 'message': 'Grade approved.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_reject(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    return Response({'success': True, 'message': 'Grade rejected.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def grade_delete(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    from apps.grading.models import GradingReport
    g = get_object_or_404(GradingReport, pk=pk)
    g.delete()
    return Response({'success': True, 'message': 'Grade deleted.'})


# ── Activity Log ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_list(request):
    guard = _admin_only(request)
    if guard: return guard
    # Build activity from real DB events
    activities = []

    from apps.requests.models import SupervisorRequest
    for r in SupervisorRequest.objects.select_related('team', 'leader').order_by('-created_at')[:50]:
        activities.append({
            'action':       f'Supervisor request {r.status}',
            'description':  f'{r.team.name if r.team else "Team"} requested supervisor for "{r.project_idea}"',
            'created_at':   r.created_at.isoformat(),
            'related_type': 'proposal',
            'created_by':   r.leader.display_name if r.leader else 'Student',
        })

    from apps.teams.models import Team
    for t in Team.objects.select_related('leader').order_by('-created_at')[:30]:
        activities.append({
            'action':       'Team created',
            'description':  f'Team "{t.name}" created with project "{t.project_title}"',
            'created_at':   t.created_at.isoformat(),
            'related_type': 'team',
            'created_by':   t.leader.display_name if t.leader else 'Student',
        })

    from apps.grading.models import GradingReport
    for g in GradingReport.objects.select_related('team', 'supervisor').order_by('-created_at')[:20]:
        activities.append({
            'action':       'Grade submitted',
            'description':  f'{g.team.name if g.team else "Team"} — Final grade: {float(g.final_grade):.1f}%',
            'created_at':   g.created_at.isoformat(),
            'related_type': 'defense',
            'created_by':   g.supervisor.display_name if g.supervisor else 'Supervisor',
        })

    activities.sort(key=lambda x: x['created_at'], reverse=True)
    return Response({'success': True, 'activities': activities[:100]})


# ── Students (admin CRUD) ──────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def students_list(request):
    guard = _admin_only(request)
    if guard: return guard
    if request.method == 'POST':
        email = (request.data.get('email') or '').strip().lower()
        name  = request.data.get('name', email)
        if not email:
            return Response({'error': 'Email is required.'}, status=400)
        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'User with this email already exists.'}, status=400)
        s = User.objects.create_user(email=email, password='Student0*', display_name=name, role='student', is_active=True)
        return Response({'success': True, 'message': f'Student {name} created.', 'id': s.id}, status=201)

    students = User.objects.filter(role='student', is_active=True).order_by('display_name')
    data = [{
        'id':    s.id,
        'name':  s.display_name,
        'sid':   s.email,
        'team':  '—',
        'supervisor': '—',
        'status': 'Active',
        'gpa':   '-',
    } for s in students]
    return Response({'success': True, 'students': data})


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def student_detail(request, pk):
    guard = _admin_only(request)
    if guard: return guard
    student = get_object_or_404(User, pk=pk, role='student')
    if request.method == 'DELETE':
        student.delete()
        return Response({'success': True, 'message': 'Student deleted.'})
    if request.method == 'PUT':
        if 'name' in request.data and request.data['name']:
            student.display_name = request.data['name'].strip()
        if 'email' in request.data and request.data['email']:
            email = request.data['email'].strip().lower()
            if not User.objects.filter(email__iexact=email).exclude(pk=student.pk).exists():
                student.email = email
        student.save()
        return Response({'success': True, 'message': 'Student updated.'})
