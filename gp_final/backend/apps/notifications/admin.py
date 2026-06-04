from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('recipient', 'title', 'notif_type', 'team_name', 'is_read', 'created_at')
    list_filter   = ('notif_type', 'is_read')
    search_fields = ('recipient__display_name', 'title', 'team_name')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Mark selected notifications as read'
