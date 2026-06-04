from django.db import models
from django.conf import settings


class TeamFile(models.Model):
    """
    A file submitted by a student (or simulated) for a team.
    Triggers a supervisor notification on creation.
    """
    team       = models.ForeignKey(
        'teams.Team',
        related_name='submitted_files',
        on_delete=models.CASCADE,
    )
    uploader   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='uploaded_files',
        on_delete=models.SET_NULL,
        null=True,
    )
    file       = models.FileField(upload_to='team_submissions/%Y/%m/')
    file_name  = models.CharField(max_length=255)          # original filename
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'files_teamfile'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.team.name} / {self.file_name}'
