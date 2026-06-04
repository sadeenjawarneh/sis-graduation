"""Central helpers for recording admin activity."""

import logging
from typing import Optional

from django.contrib.auth.models import AnonymousUser

from .models import ActivityLog

logger = logging.getLogger(__name__)


def log_activity(
    *,
    action: str,
    description: str = '',
    related_type: str,
    related_id: Optional[int] = None,
    created_by=None,
) -> Optional[ActivityLog]:
    """
    Persist an activity row. Swallows errors so logging never breaks primary workflows.
    """
    try:
        user = None
        if created_by is not None and not isinstance(created_by, AnonymousUser):
            user = created_by
        return ActivityLog.objects.create(
            action=action,
            description=description or '',
            related_type=related_type,
            related_id=related_id,
            created_by=user,
        )
    except Exception:
        logger.exception('activity.log_failed action=%s related_type=%s', action, related_type)
        return None
