from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    A notification sent to a specific user.
    Covers: supervisor requests, meeting bookings, grade publishing,
            file uploads, join requests, and supervisor comments.
    """

    class NotifType(models.TextChoices):
        SUPERVISOR_REQUEST  = 'supervisor_request',  'Supervisor Request'
        SUPERVISOR_ASSIGNED = 'supervisor_assigned',  'Supervisor Assigned'
        REQUEST_REJECTED    = 'request_rejected',    'Request Rejected'
        MEETING_SCHEDULED   = 'meeting_scheduled',   'Meeting Scheduled'
        MEETING_BOOKED      = 'meeting_booked',      'Meeting Booked'
        GRADE_PUBLISHED     = 'grade_published',     'Grade Published'
        REPORT_SAVED        = 'report_saved',        'Report Saved'
        FILE_UPLOADED       = 'file_uploaded',       'File Uploaded'
        SUPERVISOR_COMMENT  = 'supervisor_comment',  'Supervisor Comment'
        JOIN_REQUEST        = 'join_request',        'Join Request'
        JOIN_APPROVED       = 'join_approved',       'Join Approved'
        JOIN_REJECTED       = 'join_rejected',       'Join Rejected'
        GENERAL             = 'general',             'General'

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE,
    )
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    notif_type  = models.CharField(
        max_length=40,
        choices=NotifType.choices,
        default=NotifType.GENERAL,
    )
    team_name   = models.CharField(max_length=120, blank=True)   # denormalised for quick display
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.notif_type}] → {self.recipient.display_name}: {self.title}'
