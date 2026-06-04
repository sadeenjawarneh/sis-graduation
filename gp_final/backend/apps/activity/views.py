from django.http import JsonResponse

from .models import ActivityLog


def activity_api(request):
    if request.method != 'GET':
        return JsonResponse(
            {'success': False, 'message': 'Method not allowed.'},
            status=405,
        )

    rows = ActivityLog.objects.all()[:500]
    activities = [
        {
            'action': item.action,
            'description': item.description,
            'created_at': item.created_at.isoformat(),
            'related_type': item.related_type,
        }
        for item in rows
    ]
    return JsonResponse(
        {
            'success': True,
            'message': 'Activity fetched successfully.',
            'count': len(activities),
            'activities': activities,
        }
    )
