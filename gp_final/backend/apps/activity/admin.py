from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'related_type', 'related_id', 'created_at', 'created_by')
    list_filter = ('related_type', 'action')
    search_fields = ('action', 'description')
    readonly_fields = ('created_at',)
