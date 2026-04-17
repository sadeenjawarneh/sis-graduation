from django.contrib import admin
from .models import Team, Membership, TeamMessage

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    # شلنا 'status' من هون لأنها مسببة المشكلة في الموديل تبعك
    list_display = ('user', 'team', 'role') 
    list_filter = ('role', 'team')
    search_fields = ('user__username', 'team__name')

# أضيفي هاد السطر كمان عشان تشوفي المسجات في لوحة التحكم لو احتجتي
@admin.register(TeamMessage)
class TeamMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'content', 'timestamp')