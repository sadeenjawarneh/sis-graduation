from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Supervisor, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Role', {'fields': ('role',)}),)
    list_display = (*BaseUserAdmin.list_display, 'role')
    list_filter = (*BaseUserAdmin.list_filter, 'role')


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'capacity')
    search_fields = ('user__username', 'user__email', 'department')
