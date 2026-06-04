import json

from apps.activity.models import ActivityLog
from apps.activity.services import log_activity
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.models import User
from apps.teams.models import Team
from .models import Supervisor


def students_api(request):
    if request.method != 'GET':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    students = Student.objects.select_related('user', 'team', 'supervisor').all()
    data = []
    for student in students:
        team_dict = None
        if student.team_id:
            team_dict = {
                'id': student.team.id,
                'name': student.team.name,
                'project_title': student.team.project_title,
            }

        supervisor_dict = None
        if student.supervisor_id:
            supervisor_dict = {
                'id': student.supervisor_id,
                'name': student.supervisor.get_full_name() or student.supervisor.username,
            }

        data.append(
            {
                'id': student.id,
                'student_id': student.student_id,
                'username': student.user.username,
                'full_name': student.user.get_full_name(),
                'email': student.user.email,
                'gpa': float(student.gpa) if student.gpa is not None else None,
                'status': student.status,
                'team': team_dict,
                'supervisor': supervisor_dict,
            }
        )

    return JsonResponse(
        {
            'success': True,
            'message': 'Students fetched successfully.',
            'count': len(data),
            'students': data,
        }
    )


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}'), None
    except json.JSONDecodeError:
        return None, JsonResponse(
            {'success': False, 'message': 'Invalid JSON body.'},
            status=400,
        )


def _supervisor_to_dict(profile):
    return {
        'id': profile.id,
        'department': profile.department,
        'capacity': profile.capacity,
        'assigned_count': 0,
        'teams': [],
        'user': {
            'id': profile.user_id,
            'username': profile.user.username,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'email': profile.user.email,
            'role': profile.user.role,
        },
    }


def _student_to_dict(student):
    team_dict = None
    if student.team_id:
        team_dict = {
            'id': student.team.id,
            'name': student.team.name,
            'project_title': student.team.project_title,
        }

    supervisor_dict = None
    if student.supervisor_id:
        supervisor_dict = {
            'id': student.supervisor_id,
            'name': student.supervisor.get_full_name() or student.supervisor.username,
        }

    return {
        'id': student.id,
        'student_id': student.student_id,
        'username': student.user.username,
        'full_name': student.user.get_full_name(),
        'email': student.user.email,
        'gpa': float(student.gpa) if student.gpa is not None else None,
        'status': student.status,
        'team': team_dict,
        'supervisor': supervisor_dict,
    }


@csrf_exempt
def create_student_api(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    payload, error_response = _parse_json_body(request)
    if error_response:
        return error_response

    name = (payload.get('name') or '').strip()
    student_id = (payload.get('student_id') or '').strip()
    team_id = payload.get('team_id')
    supervisor_id = payload.get('supervisor_id')
    gpa = payload.get('gpa')
    status = (payload.get('status') or '').strip().lower()

    if not name:
        return JsonResponse({'success': False, 'message': 'Student name is required.'}, status=400)
    if not student_id:
        return JsonResponse({'success': False, 'message': 'Student ID is required.'}, status=400)
    if not team_id:
        return JsonResponse({'success': False, 'message': 'Team is required.'}, status=400)
    if status not in {Student.Status.ACTIVE, Student.Status.PENDING, 'active', 'pending'}:
        status = Student.Status.PENDING

    try:
        team = Team.objects.get(pk=int(team_id))
    except (ValueError, TypeError, Team.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid team.'}, status=400)

    User = get_user_model()
    try:
        supervisor_user = None
        if supervisor_id not in (None, '', 0, '0'):
            supervisor_user = User.objects.get(pk=int(supervisor_id))
            if supervisor_user.role != User.Role.SUPERVISOR:
                return JsonResponse({'success': False, 'message': 'Invalid supervisor.'}, status=400)

        # Derive username from student_id, ensure uniqueness.
        base_username = student_id
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f'{base_username}_{suffix}'

        first_name = name.split(' ')[0] if name else ''
        last_name = ' '.join(name.split(' ')[1:]) if name else ''

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=get_random_string(14),
                first_name=first_name,
                last_name=last_name,
                role=User.Role.STUDENT,
            )
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                team=team,
                supervisor=supervisor_user,
                gpa=gpa if gpa not in ('', None) else None,
                status=status,
            )
    except (IntegrityError, ValueError) as error:
        return JsonResponse(
            {'success': False, 'message': f'Failed to create student: {error}.'},
            status=400,
        )

    student = Student.objects.select_related('user', 'team', 'supervisor').get(pk=student.pk)
    log_activity(
        action='Student Created',
        description=f"Student '{student.user.get_full_name() or student.user.username}' (ID {student.id}) added to team '{student.team.name}'.",
        related_type=ActivityLog.RelatedType.STUDENT,
        related_id=student.id,
        created_by=request.user,
    )
    return JsonResponse(
        {
            'success': True,
            'message': 'Created successfully',
            'data': _student_to_dict(student),
        },
        status=201,
    )


@csrf_exempt
def student_detail_api(request, student_id):
    try:
        student = Student.objects.select_related('user', 'team', 'supervisor').get(pk=student_id)
    except Student.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Student not found.'},
            status=404,
        )

    if request.method == 'PUT':
        payload, error_response = _parse_json_body(request)
        if error_response:
            return error_response

        name = (payload.get('name') or '').strip()
        sid = (payload.get('student_id') or '').strip()
        team_id = payload.get('team_id')
        supervisor_id = payload.get('supervisor_id')
        gpa = payload.get('gpa')
        status = (payload.get('status') or '').strip().lower()

        if not name:
            return JsonResponse({'success': False, 'message': 'Student name is required.'}, status=400)
        if not sid:
            return JsonResponse({'success': False, 'message': 'Student ID is required.'}, status=400)
        if not team_id:
            return JsonResponse({'success': False, 'message': 'Team is required.'}, status=400)
        if status not in {Student.Status.ACTIVE, Student.Status.PENDING, 'active', 'pending'}:
            status = Student.Status.PENDING

        try:
            team = Team.objects.get(pk=int(team_id))
        except (ValueError, TypeError, Team.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid team.'}, status=400)

        User = get_user_model()
        supervisor_user = None
        try:
            if supervisor_id not in (None, '', 0, '0'):
                supervisor_user = User.objects.get(pk=int(supervisor_id))
                if supervisor_user.role != User.Role.SUPERVISOR:
                    return JsonResponse({'success': False, 'message': 'Invalid supervisor.'}, status=400)
        except (ValueError, TypeError, User.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid supervisor.'}, status=400)

        first_name = name.split(' ')[0] if name else ''
        last_name = ' '.join(name.split(' ')[1:]) if name else ''

        with transaction.atomic():
            student.user.first_name = first_name
            student.user.last_name = last_name
            student.user.save(update_fields=['first_name', 'last_name'])

            student.student_id = sid
            student.team = team
            student.supervisor = supervisor_user
            student.gpa = gpa if gpa not in ('', None) else None
            student.status = status
            student.save()

        student = Student.objects.select_related('user', 'team', 'supervisor').get(pk=student.pk)
        return JsonResponse(
            {
                'success': True,
                'message': 'Student updated successfully.',
                'data': _student_to_dict(student),
            }
        )

    if request.method == 'DELETE':
        sid = student.id
        sname = student.user.get_full_name() or student.user.username
        with transaction.atomic():
            user = student.user
            student.delete()
            # avoid orphan user accounts for deleted students
            user.delete()

        log_activity(
            action='Student Deleted',
            description=f"Student '{sname}' (ID {sid}) was deleted.",
            related_type=ActivityLog.RelatedType.STUDENT,
            related_id=sid,
            created_by=request.user,
        )
        return JsonResponse(
            {'success': True, 'message': 'Student deleted successfully.'}
        )

    return JsonResponse(
        {'success': False, 'message': 'Method not allowed.'},
        status=405,
    )


@csrf_exempt
def supervisors_api(request):
    if request.method == 'GET':
        profiles = list(Supervisor.objects.select_related('user').all())

        user_ids = [p.user_id for p in profiles]
        teams = Team.objects.filter(supervisor_id__in=user_ids).only('id', 'name', 'supervisor_id')
        teams_by_supervisor = {}
        for t in teams:
            teams_by_supervisor.setdefault(t.supervisor_id, []).append(
                {
                    'id': t.id,
                    'name': t.name,
                }
            )

        data = []
        for profile in profiles:
            item = _supervisor_to_dict(profile)
            assigned_teams = teams_by_supervisor.get(profile.user_id, [])
            item['teams'] = assigned_teams
            item['assigned_count'] = len(assigned_teams)
            data.append(item)

        return JsonResponse(
            {
                'success': True,
                'message': 'Supervisors fetched successfully.',
                'count': len(data),
                'supervisors': data,
            }
        )

    if request.method == 'POST':
        # Reuse the same creation logic currently used by /api/supervisors/create/
        return create_supervisor_api(request)

    return JsonResponse(
        {'success': False, 'message': 'Method not allowed.'},
        status=405,
    )


@csrf_exempt
def create_supervisor_api(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    payload, error_response = _parse_json_body(request)
    if error_response:
        return error_response

    first_name = (payload.get('first_name') or '').strip()
    last_name = (payload.get('last_name') or '').strip()
    email = (payload.get('email') or '').strip()
    department = (payload.get('department') or '').strip()
    raw_capacity = payload.get('capacity')

    if not first_name:
        return JsonResponse({'success': False, 'message': 'First name is required.'}, status=400)
    if not last_name:
        return JsonResponse({'success': False, 'message': 'Last name is required.'}, status=400)
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

    # Allow clients to provide username, but auto-generate when omitted.
    username = (payload.get('username') or '').strip()

    User = get_user_model()
    try:
        capacity = int(raw_capacity or 0)
        if capacity < 0:
            return JsonResponse({'success': False, 'message': 'Capacity must be zero or greater.'}, status=400)

        if not username:
            base_username = f"{first_name}.{last_name}".lower().replace(' ', '') or "supervisor"
            base_username = ''.join(ch for ch in base_username if ch.isalnum() or ch in {'_', '.'}) or "supervisor"
            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                suffix += 1
                username = f'{base_username}{suffix}'

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=get_random_string(20),
                first_name=first_name,
                last_name=last_name,
                role=User.Role.SUPERVISOR,
            )
            profile = Supervisor.objects.create(
                user=user,
                department=department,
                capacity=capacity,
            )
    except ValueError:
        return JsonResponse(
            {'success': False, 'message': 'Capacity must be a number.'},
            status=400,
        )
    except IntegrityError as error:
        return JsonResponse(
            {'success': False, 'message': f'Failed to create supervisor: {error}.'},
            status=400,
        )

    log_activity(
        action='Supervisor Added',
        description=f"Supervisor '{profile.user.get_full_name() or profile.user.username}' (profile ID {profile.id}) was added.",
        related_type=ActivityLog.RelatedType.SUPERVISOR,
        related_id=profile.id,
        created_by=request.user,
    )
    return JsonResponse(
        {
            'success': True,
            'message': 'Created successfully',
            'data': _supervisor_to_dict(profile),
        },
        status=201,
    )


@csrf_exempt
def supervisor_detail_api(request, supervisor_id):
    try:
        profile = Supervisor.objects.select_related('user').get(pk=supervisor_id)
    except Supervisor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Supervisor not found.'}, status=404)

    if request.method == 'PUT':
        payload, error_response = _parse_json_body(request)
        if error_response:
            return error_response

        first_name = (payload.get('first_name') or '').strip()
        last_name = (payload.get('last_name') or '').strip()
        email = (payload.get('email') or '').strip()
        department = (payload.get('department') or '').strip()
        raw_capacity = payload.get('capacity')

        if not first_name:
            return JsonResponse({'success': False, 'message': 'First name is required.'}, status=400)
        if not last_name:
            return JsonResponse({'success': False, 'message': 'Last name is required.'}, status=400)
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

        try:
            capacity = int(raw_capacity or 0)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Capacity must be a number.'}, status=400)
        if capacity < 0:
            return JsonResponse({'success': False, 'message': 'Capacity must be zero or greater.'}, status=400)

        assigned_count = Team.objects.filter(supervisor_id=profile.user_id).count()
        if capacity < assigned_count:
            return JsonResponse(
                {
                    'success': False,
                    'message': f'Capacity cannot be less than currently assigned teams ({assigned_count}).',
                },
                status=400,
            )

        with transaction.atomic():
            profile.user.first_name = first_name
            profile.user.last_name = last_name
            profile.user.email = email
            profile.user.save(update_fields=['first_name', 'last_name', 'email'])

            profile.department = department
            profile.capacity = capacity
            profile.save(update_fields=['department', 'capacity'])

        profile = Supervisor.objects.select_related('user').get(pk=profile.pk)
        item = _supervisor_to_dict(profile)
        item['assigned_count'] = assigned_count
        item['teams'] = [
            {'id': t.id, 'name': t.name}
            for t in Team.objects.filter(supervisor_id=profile.user_id).only('id', 'name')
        ]

        log_activity(
            action='Supervisor Edited',
            description=f"Supervisor '{profile.user.get_full_name() or profile.user.username}' (profile ID {profile.id}) was updated.",
            related_type=ActivityLog.RelatedType.SUPERVISOR,
            related_id=profile.id,
            created_by=request.user,
        )
        return JsonResponse(
            {
                'success': True,
                'message': 'Supervisor updated successfully.',
                'data': item,
            }
        )

    if request.method == 'DELETE':
        assigned_count = Team.objects.filter(supervisor_id=profile.user_id).count()
        if assigned_count > 0:
            return JsonResponse(
                {
                    'success': False,
                    'message': 'Cannot delete supervisor while assigned to teams.',
                },
                status=400,
            )

        spid = profile.id
        sname = profile.user.get_full_name() or profile.user.username
        with transaction.atomic():
            user = profile.user
            profile.delete()
            user.delete()

        log_activity(
            action='Supervisor Deleted',
            description=f"Supervisor '{sname}' (profile ID {spid}) was deleted.",
            related_type=ActivityLog.RelatedType.SUPERVISOR,
            related_id=spid,
            created_by=request.user,
        )
        return JsonResponse({'success': True, 'message': 'Supervisor deleted successfully.'})

    return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)
