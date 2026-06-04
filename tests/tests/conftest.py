"""
Shared fixtures for all pytest-django tests.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


# ── API client ────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client):
    """Returns a helper that creates an authenticated APIClient for a user."""
    def _make(user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client
    return _make


# ── User factories ────────────────────────────────────────────────────────────

@pytest.fixture
def make_student(db):
    counter = [0]
    def _make(email=None, password='Test1234!', display_name=None):
        counter[0] += 1
        email = email or f'student{counter[0]}@cit.just.edu.jo'
        display_name = display_name or f'Student{counter[0]}'
        u = User.objects.create_user(
            email=email, password=password,
            display_name=display_name, role='student',
        )
        return u
    return _make


@pytest.fixture
def make_supervisor(db):
    counter = [0]
    def _make(email=None, password='Test1234!', display_name=None):
        counter[0] += 1
        email = email or f'supervisor{counter[0]}@just.edu.jo'
        display_name = display_name or f'Supervisor{counter[0]}'
        u = User.objects.create_user(
            email=email, password=password,
            display_name=display_name, role='supervisor',
            department='CS', expertise='AI',
        )
        return u
    return _make


@pytest.fixture
def make_admin(db):
    def _make(email='admin@just.edu.jo', password='Admin@GP2025'):
        return User.objects.create_superuser(
            email=email, password=password,
            display_name='Admin', role='admin',
        )
    return _make


# ── Team factory ──────────────────────────────────────────────────────────────

@pytest.fixture
def make_team(db):
    from apps.teams.models import Team
    counter = [0]
    def _make(leader, name=None, supervisor=None, status='forming'):
        counter[0] += 1
        name = name or f'Test Team {counter[0]}'
        team = Team.objects.create(
            name=name,
            project_title=name,
            project_description='Test project',
            leader=leader,
            assigned_supervisor=supervisor,
            status=status,
        )
        team.members.add(leader)
        return team
    return _make


# ── Seeded users (match seed_data.py) ────────────────────────────────────────

@pytest.fixture
def seeded_supervisor(db):
    u = User.objects.create_user(
        email='Hamza@just.edu.jo', password='Hamza0*',
        display_name='Hamza Alkofahi', role='supervisor',
        department='Computer Science', expertise='AI,ML',
    )
    return u


@pytest.fixture
def seeded_student(db):
    u = User.objects.create_user(
        email='sadeen@cit.just.edu.jo', password='Sadeen0*',
        display_name='Sadeen', role='student',
    )
    return u
