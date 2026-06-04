from django.conf import settings
from django.db import models


class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        UNDER_REVIEW = 'under_review', 'Under review'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='proposals')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='proposals_as_supervisor', limit_choices_to={'role': 'supervisor'})
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='proposals/%Y/%m/', blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'apps.proposals'
        ordering = ['-submitted_at', '-pk']

    def __str__(self):
        return self.title
