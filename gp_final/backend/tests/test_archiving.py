"""
Archiving Tests — mirrors archiving.cy.js
TC-1  PATCH team status to 'complete' → 200
TC-2  GET teams returns completed team
TC-3  Team detail has required fields
TC-4  Old team (any date) still returned
TC-5  Project description update persists (backup test)
"""
import pytest

TEAMS_URL = '/api/v1/teams/'


@pytest.mark.django_db
class TestArchiving:

    def test_TC1_patch_status_to_complete(self, client, auth_client, make_student, make_supervisor, make_team):
        sup = make_supervisor()
        student = make_student()
        team = make_team(leader=student, supervisor=sup)
        ac = auth_client(sup)
        res = ac.patch(f'{TEAMS_URL}{team.id}/', {'status': 'complete'})
        assert res.status_code == 200
        assert res.data['status'] == 'complete'

    def test_TC2_completed_team_in_list(self, client, auth_client, make_student, make_supervisor, make_team):
        sup = make_supervisor()
        student = make_student()
        team = make_team(leader=student, supervisor=sup, status='complete')
        ac = auth_client(sup)
        res = ac.get(TEAMS_URL)
        assert res.status_code == 200
        assert any(t['id'] == team.id for t in res.data)

    def test_TC3_team_detail_has_required_fields(self, client, auth_client, make_student, make_team):
        student = make_student()
        team = make_team(leader=student)
        ac = auth_client(student)
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.status_code == 200
        for field in ('id', 'name', 'project_title', 'status', 'created_at'):
            assert field in res.data, f'Missing field: {field}'

    def test_TC5_description_update_persists(self, client, auth_client, make_student, make_supervisor, make_team):
        sup = make_supervisor()
        student = make_student()
        team = make_team(leader=student, supervisor=sup)
        ac = auth_client(sup)
        original_title = team.project_title
        ac.patch(f'{TEAMS_URL}{team.id}/', {'project_description': 'Updated for backup test.'})
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.data['project_title'] == original_title
        assert res.data['project_description'] == 'Updated for backup test.'

    def test_TC2_admin_can_search_archive(self, client, auth_client, make_student, make_supervisor, make_team, make_admin):
        """TC-2: Admin searches archive → completed team retrieved."""
        admin = make_admin()
        sup = make_supervisor()
        student = make_student()
        team = make_team(leader=student, supervisor=sup, status='complete')
        ac = auth_client(admin)
        res = ac.get(TEAMS_URL)
        assert res.status_code == 200
        ids = [t['id'] for t in res.data]
        assert team.id in ids

    def test_TC2_admin_sees_all_teams_including_completed(self, client, auth_client, make_student, make_supervisor, make_team, make_admin):
        """TC-2: Admin gets all teams including completed ones."""
        admin = make_admin()
        sup = make_supervisor()
        s1, s2 = make_student(), make_student()
        active_team = make_team(leader=s1, supervisor=sup, status='active')
        completed_team = make_team(leader=s2, supervisor=sup, status='complete')
        ac = auth_client(admin)
        res = ac.get(TEAMS_URL)
        ids = [t['id'] for t in res.data]
        assert active_team.id in ids
        assert completed_team.id in ids

    def test_TC4_old_team_still_returned(self, client, auth_client, make_student, make_supervisor, make_team):
        from django.utils import timezone
        from datetime import timedelta
        sup = make_supervisor()
        student = make_student()
        team = make_team(leader=student, supervisor=sup)
        # Simulate old team by changing created_at
        from apps.teams.models import Team
        Team.objects.filter(pk=team.pk).update(created_at=timezone.now() - timedelta(days=365*6))
        ac = auth_client(sup)
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.status_code == 200
        assert res.data['id'] == team.id
