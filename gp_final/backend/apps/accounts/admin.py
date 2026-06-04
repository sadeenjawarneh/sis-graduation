from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as Base
from .models import User

@admin.register(User)
class UserAdmin(Base):
    list_display   = ('email', 'display_name', 'role', 'department', 'is_active')
    list_filter    = ('role', 'is_active')
    search_fields  = ('email', 'display_name')
    ordering       = ('display_name',)
    fieldsets      = (
        (None,          {'fields': ('email', 'password')}),
        ('Info',        {'fields': ('display_name', 'role', 'department', 'expertise', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets  = (
        (None, {'classes': ('wide',), 'fields': ('email', 'display_name', 'role', 'password1', 'password2')}),
    )
