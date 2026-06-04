"""
Team Management Tests — mirrors creat_team.cy.js & team_change.cy.js
TC-T1  Create team page API available
TC-T2  Valid team name accepted
TC-T3  Team created successfully
TC-T4  Description field accepted
TC-T5  Only students can create teams
TC-T6  Leader shown in team members
TC-T7  Join request sent successfully (201)
TC-T8  Already in team → 400
TC-T9  Leave team works
TC-1   Join request allowed when team has vacancy
TC-2   Full team (5) rejects join request
TC-3   Approved vote adds student to team
TC-4   Rejected vote sends notification
TC-7   members_count returned in team detail
TC-9   Student leaves and joins another team
"""
import pytest

TEAMS_URL    = '/api/v1/teams/'
MY_TEAM_URL  = '/api/v1/teams/my/'


@pytest.mark.django_db
class TestTeamCreation:

    def test_TC_T2_valid_team_name_creates_team(self, client, auth_client, make_student):
        student = make_student()
        ac = auth_client(student)
        res = ac.post(TEAMS_URL, {'name': 'Smart City System', 'description': 'A smart city project'})
        assert res.status_code == 201
        assert res.data['name'] == 'Smart City System'

    def test_TC_T3_team_created_with_leader(self, client, auth_client, make_student):
        student = make_student()
        ac = auth_client(student)
        res = ac.post(TEAMS_URL, {'name': 'Alpha Team', 'description': 'Test'})
        assert res.status_code == 201
        assert res.data['leader']['id'] == student.id

    def test_TC_T4_description_stored_correctly(self, client, auth_client, make_student):
        student = make_student()
        ac = auth_client(student)
        desc = 'This project aims to build a smart city monitoring system.'
        res = ac.post(TEAMS_URL, {'name': 'My Team', 'description': desc})
        assert res.status_code == 201
        assert res.data['project_description'] == desc

    def test_TC_T5_supervisor_cannot_create_team(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(TEAMS_URL, {'name': 'Sup Team', 'description': 'Test'})
        assert res.status_code == 400

    def test_TC_T8_student_already_in_team_gets_400(self, client, auth_client, make_student, make_team):
        student = make_student()
        make_team(leader=student)
        ac = auth_client(student)
        res = ac.post(TEAMS_URL, {'name': 'Second Team', 'description': 'Test'})
        assert res.status_code == 400
        assert 'already belong' in res.data['error'].lower()

    def test_TC_T6_leader_shown_in_members(self, client, auth_client, make_student):
        student = make_student()
        ac = auth_client(student)
        res = ac.post(TEAMS_URL, {'name': 'Leader Team', 'description': 'Test'})
        assert res.status_code == 201
        member_ids = [m['id'] for m in res.data['members']]
        assert student.id in member_ids

    def test_members_count_in_team_detail(self, client, auth_client, make_student, make_team):
        student = make_student()
        team = make_team(leader=student)
        ac = auth_client(student)
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.status_code == 200
        assert res.data['members_count'] == 1

    def test_supervisor_field_is_null_when_unassigned(self, client, auth_client, make_student, make_team):
        student = make_student()
        team = make_team(leader=student)
        ac = auth_client(student)
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.data['supervisor'] is None

    def test_supervisor_field_set_after_assignment(self, client, auth_client, make_student, make_supervisor, make_team):
        student = make_student()
        sup = make_supervisor()
        team = make_team(leader=student, supervisor=sup)
        ac = auth_client(student)
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.data['supervisor'] == sup.id


@pytest.mark.django_db
class TestJoinRequests:

    def test_TC1_join_request_allowed_when_vacancy(self, client, auth_client, make_student, make_team):
        leader = make_student()
        joiner = make_student()
        team = make_team(leader=leader)
        ac = auth_client(joiner)
        res = ac.post(f'{TEAMS_URL}{team.id}/join-requests/')
        assert res.status_code == 201
        assert res.data['status'] == 'pending'

    def test_TC2_full_team_rejects_join(self, client, auth_client, make_student, make_team):
        members = [make_student() for _ in range(5)]
        leader = members[0]
        team = make_team(leader=leader)
        for m in members[1:]:
            team.members.add(m)
        outsider = make_student()
        ac = auth_client(outsider)
        res = ac.post(f'{TEAMS_URL}{team.id}/join-requests/')
        assert res.status_code == 400

    def test_TC3_approved_vote_adds_student(self, client, auth_client, make_student, make_team):
        leader = make_student()
        joiner = make_student()
        team = make_team(leader=leader)
        # Send join request
        ac_joiner = auth_client(joiner)
        req_res = ac_joiner.post(f'{TEAMS_URL}{team.id}/join-requests/')
        req_id = req_res.data['id']
        # Leader votes yes
        ac_leader = auth_client(leader)
        vote_res = ac_leader.post(f'{TEAMS_URL}join-requests/{req_id}/vote/', {'vote': 'yes'})
        assert vote_res.status_code == 200
        assert vote_res.data['new_status'] == 'accepted'
        team.refresh_from_db()
        assert team.members.filter(pk=joiner.pk).exists()

    def test_TC4_rejected_vote_sends_notification(self, client, auth_client, make_student, make_team):
        from apps.notifications.models import Notification
        leader = make_student()
        joiner = make_student()
        team = make_team(leader=leader)
        ac_joiner = auth_client(joiner)
        req_res = ac_joiner.post(f'{TEAMS_URL}{team.id}/join-requests/')
        req_id = req_res.data['id']
        ac_leader = auth_client(leader)
        vote_res = ac_leader.post(f'{TEAMS_URL}join-requests/{req_id}/vote/', {'vote': 'no'})
        assert vote_res.data['new_status'] == 'rejected'
        assert Notification.objects.filter(recipient=joiner).exists()

    def test_TC9_student_leaves_and_joins_another_team(self, client, auth_client, make_student, make_team):
        student = make_student()
        other_leader = make_student()
        source_team = make_team(leader=student)
        target_team = make_team(leader=other_leader)
        ac = auth_client(student)
        # Leave source team
        leave_res = ac.post(f'{TEAMS_URL}{source_team.id}/leave/')
        assert leave_res.status_code == 200
        # Send join request to target
        join_res = ac.post(f'{TEAMS_URL}{target_team.id}/join-requests/')
        assert join_res.status_code == 201
        assert join_res.data['status'] == 'pending'


@pytest.mark.django_db
class TestTeamChangeBoundary:
    """TC-7, TC-8, TC-10 — additional boundary/state tests."""

    def test_TC7_team_full_join_disabled(self, client, auth_client, make_student, make_team):
        """TC-7: Team at 5 members → join returns 400."""
        members = [make_student() for _ in range(5)]
        team = make_team(leader=members[0])
        for m in members[1:]:
            team.members.add(m)
        outsider = make_student()
        ac = auth_client(outsider)
        res = ac.post(f'{TEAMS_URL}{team.id}/join-requests/')
        assert res.status_code == 400

    def test_TC7_members_count_reflects_full_team(self, client, auth_client, make_student, make_team):
        """TC-7: members_count == 5 → team is full."""
        members = [make_student() for _ in range(5)]
        team = make_team(leader=members[0])
        for m in members[1:]:
            team.members.add(m)
        ac = auth_client(members[0])
        res = ac.get(f'{TEAMS_URL}{team.id}/')
        assert res.data['members_count'] == 5

    def test_TC8_disbanded_team_rejects_join(self, client, auth_client, make_student, make_team):
        """TC-8: Disbanded/completed team rejects join requests."""
        leader = make_student()
        team = make_team(leader=leader, status='disbanded')
        outsider = make_student()
        ac = auth_client(outsider)
        res = ac.post(f'{TEAMS_URL}{team.id}/join-requests/')
        # disbanded teams are excluded from student GET, and join blocked
        assert res.status_code in (400, 403, 404)


@pytest.mark.django_db
class TestMyTeam:

    def test_my_team_returns_404_when_not_in_team(self, client, auth_client, make_student):
        student = make_student()
        ac = auth_client(student)
        res = ac.get(MY_TEAM_URL)
        assert res.status_code == 404

    def test_my_team_returns_team_when_in_one(self, client, auth_client, make_student, make_team):
        student = make_student()
        team = make_team(leader=student)
        ac = auth_client(student)
        res = ac.get(MY_TEAM_URL)
        assert res.status_code == 200
        assert res.data['id'] == team.id
