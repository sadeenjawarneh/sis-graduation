"""
push_notification() is the single entry point for creating a Notification record.
Every app imports this helper so notification logic stays in one place.
"""

from .models import Notification


def push_notification(
    recipient_id: int,
    title: str,
    message: str,
    notif_type: str = 'general',
    team_name: str = '',
) -> Notification:
    """
    Create and persist a Notification for the given recipient user PK.

    Args:
        recipient_id: PK of the User who should receive this notification.
        title:        Short headline, e.g. 'Meeting scheduled'.
        message:      Full notification body.
        notif_type:   One of Notification.NotifType values (string).
        team_name:    Optional team name for quick display (denormalised).

    Returns:
        The newly created Notification instance.
    """
    return Notification.objects.create(
        recipient_id=recipient_id,
        title=title,
        message=message,
        notif_type=notif_type,
        team_name=team_name,
    )
