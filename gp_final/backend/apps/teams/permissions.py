from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsSupervisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.SUPERVISOR


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.STUDENT


class IsTeamLeader(BasePermission):
    """Object-level: only the team's leader may modify it."""
    def has_object_permission(self, request, view, obj):
        return obj.leader == request.user


class IsSupervisorOfTeam(BasePermission):
    """Object-level: only the assigned supervisor of the team."""
    def has_object_permission(self, request, view, obj):
        return obj.assigned_supervisor == request.user
