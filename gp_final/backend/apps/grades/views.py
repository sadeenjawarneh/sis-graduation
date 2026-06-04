import json

from apps.activity.models import ActivityLog
from apps.activity.services import log_activity
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Grade


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}'), None
    except json.JSONDecodeError:
        return None, JsonResponse(
            {'success': False, 'message': 'Invalid JSON body.'},
            status=400,
        )


def _grade_to_dict(grade):
    return {
        'id': grade.id,
        'team_id': grade.team_id,
        'team_name': grade.team.name,
        'project_title': grade.team.project_title,
        'supervisor_name': grade.team.supervisor.get_full_name() if grade.team.supervisor else None,
        'supervisor_grade': float(grade.supervisor_grade) if grade.supervisor_grade is not None else None,
        'committee1_grade': float(grade.committee1_grade) if grade.committee1_grade is not None else None,
        'committee2_grade': float(grade.committee2_grade) if grade.committee2_grade is not None else None,
        'final_grade': float(grade.final_grade) if grade.final_grade is not None else None,
        'letter_grade': grade.letter_grade,
        'status': grade.status,
        'created_at': grade.created_at.isoformat() if grade.created_at else None,
        'updated_at': grade.updated_at.isoformat() if grade.updated_at else None,
    }


@csrf_exempt
def grades_api(request):
    if request.method == 'GET':
        # Get all teams and ensure each has a grade object
        from apps.teams.models import Team
        teams = Team.objects.select_related('supervisor').all()
        
        grades_data = []
        for team in teams:
            # Get or create grade for this team
            grade, created = Grade.objects.get_or_create(
                team=team,
                defaults={
                    'status': Grade.Status.DRAFT,
                    'created_by': request.user if request.user.is_authenticated else None,
                }
            )
            
            # Build grade data with team information
            grade_data = {
                'team_id': team.id,
                'team_name': team.name,
                'project_title': team.project_title,
                'supervisor_name': team.supervisor.get_full_name() if team.supervisor else None,
                'supervisor_grade': float(grade.supervisor_grade) if grade.supervisor_grade is not None else None,
                'committee1_grade': float(grade.committee1_grade) if grade.committee1_grade is not None else None,
                'committee2_grade': float(grade.committee2_grade) if grade.committee2_grade is not None else None,
                'final_grade': float(grade.final_grade) if grade.final_grade is not None else None,
                'letter_grade': grade.letter_grade,
                'status': grade.status,
                'created_at': grade.created_at.isoformat() if grade.created_at else None,
                'updated_at': grade.updated_at.isoformat() if grade.updated_at else None,
            }
            
            # Include grade ID if it exists (for edit/delete operations)
            if not created:
                grade_data['id'] = grade.id
            
            grades_data.append(grade_data)
        
        return JsonResponse(
            {
                'success': True,
                'message': 'Grades fetched successfully.',
                'count': len(grades_data),
                'grades': grades_data,
            }
        )

    if request.method == 'POST':
        return create_grade_api(request)

    return JsonResponse(
        {'success': False, 'message': 'Method not allowed.'},
        status=405,
    )


@csrf_exempt
def create_grade_api(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    payload, error_response = _parse_json_body(request)
    if error_response:
        return error_response

    team_id = payload.get('team_id')
    supervisor_grade = payload.get('supervisor_grade')
    committee1_grade = payload.get('committee1_grade')
    committee2_grade = payload.get('committee2_grade')
    status = payload.get('status', Grade.Status.DRAFT)

    if not team_id:
        return JsonResponse({'success': False, 'message': 'Team is required.'}, status=400)

    # Validate grade inputs
    if supervisor_grade is not None and (supervisor_grade < 0 or supervisor_grade > 100):
        return JsonResponse({'success': False, 'message': 'Supervisor grade must be between 0 and 100.'}, status=400)
    if committee1_grade is not None and (committee1_grade < 0 or committee1_grade > 100):
        return JsonResponse({'success': False, 'message': 'Committee Doctor 1 grade must be between 0 and 100.'}, status=400)
    if committee2_grade is not None and (committee2_grade < 0 or committee2_grade > 100):
        return JsonResponse({'success': False, 'message': 'Committee Doctor 2 grade must be between 0 and 100.'}, status=400)

    try:
        from apps.teams.models import Team
        team = Team.objects.get(pk=int(team_id))
    except (ValueError, TypeError, Team.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid team.'}, status=400)

    try:
        with transaction.atomic():
            # Get or create grade for this team
            grade, created = Grade.objects.get_or_create(
                team=team,
                defaults={
                    'supervisor_grade': supervisor_grade,
                    'committee1_grade': committee1_grade,
                    'committee2_grade': committee2_grade,
                    'status': status,
                    'created_by': request.user,
                }
            )
            
            if not created:
                # Update existing grade
                grade.supervisor_grade = supervisor_grade
                grade.committee1_grade = committee1_grade
                grade.committee2_grade = committee2_grade
                grade.status = status
                grade.save()
                
                action = 'Grade Updated'
                description = f"Grade for team '{grade.team.name}' (ID {grade.id}) was updated."
            else:
                action = 'Grade Created'
                description = f"Grade for team '{grade.team.name}' (ID {grade.id}) was created."
            
    except IntegrityError as error:
        return JsonResponse(
            {'success': False, 'message': f'Failed to save grade: {error}.'},
            status=400,
        )

    log_activity(
        action=action,
        description=description,
        related_type=ActivityLog.RelatedType.TEAM,
        related_id=grade.team.id,
        created_by=request.user,
    )
    return JsonResponse(
        {
            'success': True,
            'message': f'Grade {"created" if created else "updated"} successfully.',
            'grade': _grade_to_dict(grade),
        },
        status=201 if created else 200,
    )


@csrf_exempt
def grade_detail_api(request, grade_id):
    try:
        grade = Grade.objects.select_related('team', 'team__supervisor').get(pk=grade_id)
    except Grade.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Grade not found.'},
            status=404,
        )

    if request.method == 'PUT':
        payload, error_response = _parse_json_body(request)
        if error_response:
            return error_response

        supervisor_grade = payload.get('supervisor_grade')
        committee1_grade = payload.get('committee1_grade')
        committee2_grade = payload.get('committee2_grade')
        status = payload.get('status')

        with transaction.atomic():
            if supervisor_grade is not None:
                grade.supervisor_grade = supervisor_grade
            if committee1_grade is not None:
                grade.committee1_grade = committee1_grade
            if committee2_grade is not None:
                grade.committee2_grade = committee2_grade
            if status is not None:
                grade.status = status
            
            grade.save()

        log_activity(
            action='Grade Updated',
            description=f"Grade for team '{grade.team.name}' (ID {grade.id}) was updated.",
            related_type=ActivityLog.RelatedType.TEAM,
            related_id=grade.team.id,
            created_by=request.user,
        )
        return JsonResponse(
            {
                'success': True,
                'message': 'Grade updated successfully.',
                'grade': _grade_to_dict(grade),
            }
        )

    if request.method == 'DELETE':
        team_id = grade.team.id
        team_name = grade.team.name
        with transaction.atomic():
            grade.delete()

        log_activity(
            action='Grade Deleted',
            description=f"Grade for team '{team_name}' (ID {grade_id}) was deleted.",
            related_type=ActivityLog.RelatedType.TEAM,
            related_id=team_id,
            created_by=request.user,
        )
        return JsonResponse(
            {'success': True, 'message': 'Grade deleted successfully.'}
        )

    return JsonResponse(
        {'success': False, 'message': 'Method not allowed.'},
        status=405,
    )


@csrf_exempt
def approve_grade_api(request, grade_id):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    try:
        grade = Grade.objects.select_related('team').get(pk=grade_id)
    except Grade.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Grade not found.'},
            status=404,
        )

    if (grade.supervisor_grade is None or 
        grade.committee1_grade is None or 
        grade.committee2_grade is None):
        return JsonResponse(
            {'success': False, 'message': 'Cannot approve grade with missing supervisor or committee grades.'},
            status=400,
        )

    grade.status = Grade.Status.APPROVED
    grade.save(update_fields=['status'])
    
    log_activity(
        action='Grade Approved',
        description=f"Grade for team '{grade.team.name}' (ID {grade.id}) was approved.",
        related_type=ActivityLog.RelatedType.TEAM,
        related_id=grade.team.id,
        created_by=request.user,
    )
    return JsonResponse(
        {
            'success': True,
            'message': 'Grade approved successfully.',
            'grade': _grade_to_dict(grade),
        }
    )


@csrf_exempt
def reject_grade_api(request, grade_id):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    try:
        grade = Grade.objects.select_related('team').get(pk=grade_id)
    except Grade.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Grade not found.'},
            status=404,
        )

    grade.status = Grade.Status.REJECTED
    grade.save(update_fields=['status'])
    
    log_activity(
        action='Grade Rejected',
        description=f"Grade for team '{grade.team.name}' (ID {grade.id}) was rejected.",
        related_type=ActivityLog.RelatedType.TEAM,
        related_id=grade.team.id,
        created_by=request.user,
    )
    return JsonResponse(
        {
            'success': True,
            'message': 'Grade rejected successfully.',
            'grade': _grade_to_dict(grade),
        }
    )
