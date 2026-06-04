from django.contrib import admin
from .models import SupervisorRequest

@admin.register(SupervisorRequest)
class SupervisorRequestAdmin(admin.ModelAdmin):
    list_display  = ('team', 'leader', 'target_supervisor', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('team__name', 'leader__display_name', 'target_supervisor__display_name')
    readonly_fields = ('created_at', 'decided_at')
