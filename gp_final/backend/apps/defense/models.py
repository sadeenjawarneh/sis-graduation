from django.db import models


class DefenseSchedule(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='defense_schedules')
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'apps.defense'
        ordering = ['date', 'time']

    def __str__(self):
        return f'{self.team} - {self.date} {self.time}'
