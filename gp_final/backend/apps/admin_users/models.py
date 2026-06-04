from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Supervisor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supervisor_profiles',
    )
    department = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='uniq_supervisor_user'),
        ]

    def __str__(self) -> str:
        return str(self.user)

    def clean(self) -> None:
        super().clean()
        if self.user_id and self.user.role != 'supervisor':
            raise ValidationError(
                {'user': 'Supervisor profile must be linked to a user with the supervisor role.'},
            )
