from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    class RelatedType(models.TextChoices):
        TEAM = 'team', 'Team'
        PROPOSAL = 'proposal', 'Proposal'
        SUPERVISOR = 'supervisor', 'Supervisor'
        STUDENT = 'student', 'Student'
        DEFENSE = 'defense', 'Defense'

    action = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    related_type = models.CharField(max_length=32, choices=RelatedType.choices, db_index=True)
    related_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')

    class Meta:
        app_label = 'apps.activity'
        ordering = ['-created_at', '-pk']

    def __str__(self):
        return f'{self.action} @ {self.created_at}'
