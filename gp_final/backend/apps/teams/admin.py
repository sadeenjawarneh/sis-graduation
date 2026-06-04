from django.contrib import admin
from .models import Team, ExamDate, MembershipRequest


class ExamDateInline(admin.TabularInline):
    model = ExamDate
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display  = ('name', 'project_title', 'status', 'leader', 'assigned_supervisor', 'progress')
    list_filter   = ('status', 'academic_year')
    search_fields = ('name', 'project_title')
    inlines       = [ExamDateInline]
    filter_horizontal = ('members',)


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('team', 'student', 'status', 'created_at')
    list_filter  = ('status',)
