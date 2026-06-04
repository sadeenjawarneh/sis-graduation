from django.contrib import admin
from .models import AvailabilitySlot, Meeting

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('supervisor', 'date', 'start_time', 'end_time', 'mode')
    list_filter  = ('mode',)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('supervisor', 'team', 'date', 'time', 'meeting_type')
    list_filter  = ('meeting_type',)
