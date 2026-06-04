from django.db import models
from django.conf import settings


class Message(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='messages')
    sender    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    text      = models.TextField()
    deleted   = models.BooleanField(default=False)
    edited    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        app_label = 'chat'
    def __str__(self):
        return f"[{self.team}] {self.sender}: {self.text[:40]}"
