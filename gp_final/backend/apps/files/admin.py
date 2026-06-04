from django.contrib import admin
from .models import TeamFile

@admin.register(TeamFile)
class TeamFileAdmin(admin.ModelAdmin):
    list_display  = ('team', 'uploader', 'file_name', 'created_at')
    search_fields = ('team__name', 'uploader__display_name', 'file_name')
    readonly_fields = ('created_at',)
