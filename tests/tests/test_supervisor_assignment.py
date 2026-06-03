"""
Supervisor Assignment Tests — mirrors supervisor_assignment.cy.js
TC-1  Supervisors list returned
TC-2  Supervisor request created (201) + max 3 enforced
TC-3  Supervisor accept → team assigned
TC-4  First accept → team assigned, request resolved
TC-5  Supervisor reject → team notified, other requests stay pending
TC-6  All decline → team has no supervisor
"""
import pytest

TEAMS_URL = '/api/v1/teams/'
SUP_LIST  = '/api/v1/teams/supervisors/'
INBOX_URL = '/api/v1/teams/supervisor-inbox/'
NOTIF_URL = '/api/v1/notifications/'


@pytest.mark.django_db
class TestSupervisorList:

    def test_TC1_returns_non_empty_list(self, client, auth_client, make_student, make_supervisor):
        for i in range(3):
            make_supervisor()
        student = make_student()
        ac = auth_client(student)
        res = ac.get(SUP_LIST)
        assert res.status_code == 200
        assert len(res.data) >= 3
        for sup in res.data:
            assert 'id' in sup
            assert 'display_name' in sup
            assert 'email' in sup

    def test_TC1_supervisor_email_domain(self, client, auth_client, make_student, make_supervisor):
        make_supervisor(email='test@just.edu.jo')
        student = make_student()
        ac = auth_client(student)
        res = ac.get(SUP_LIST)
        assert all('@just.edu.jo' in s['email'] for s in res.data)


@pytest.mark.django_db
class TestSupervisorRequest:

    def _create_team(self, auth_client, student):
        ac = auth_client(student)
        res = ac.post(TEAMS_URL, {'name': f'Team-{student.pk}', 'description': 'Test'})
        return res.data['id'], ac

    def test_TC2_request_created_201(self, client, auth_client, make_student, make_supervisor):
        student = make_student()
        sup = make_supervisor()
        team_id, ac = self._create_team(auth_client, student)
        res = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': 1})
        assert res.status_code == 201
        assert res.data['status'] == 'pending'
        assert int(res.data['priority']) == 1

    def test_TC2_supervisor_sees_request_in_inbox(self, client, auth_client, make_student, make_supervisor):
        student = make_student()
        sup = make_supervisor()
        team_id, ac = self._create_team(auth_client, student)
        ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': 1})
        sup_ac = auth_client(sup)
        inbox = sup_ac.get(INBOX_URL)
        assert inbox.status_code == 200
        assert any(r['team'] == team_id for r in inbox.data)

    def test_TC2_max_3_requests_enforced(self, client, auth_client, make_student, make_supervisor):
        student = make_student()
        sups = [make_supervisor() for _ in range(4)]
        team_id, ac = self._create_team(auth_client, student)
        for i, sup in enumerate(sups[:3]):
            res = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': i+1})
            assert res.status_code == 201
        # 4th request must fail
        res = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sups[3].id, 'priority': 4})
        assert res.status_code == 400
        assert 'Maximum 3' in res.data['detail']

    def test_TC3_accept_assigns_supervisor_to_team(self, client, auth_client, make_student, make_supervisor):
        student = make_student()
        sup = make_supervisor()
        team_id, ac = self._create_team(auth_client, student)
        req_res = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': 1})
        req_id = req_res.data['id']
        sup_ac = auth_client(sup)
        respond = sup_ac.post(f'{TEAMS_URL}supervisor-requests/{req_id}/respond/', {'action': 'accept'})
        assert respond.status_code == 200
        assert respond.data['status'] == 'accepted'
        # Team should now have supervisor
        team_res = ac.get(f'{TEAMS_URL}{team_id}/')
        assert team_res.data['supervisor'] == sup.id

    def test_TC3_accept_sends_notification_to_team_members(self, client, auth_client, make_student, make_supervisor):
        from apps.notifications.models import Notification
        student = make_student()
        sup = make_supervisor()
        team_id, ac = self._create_team(auth_client, student)
        req_res = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': 1})
        req_id = req_res.data['id']
        sup_ac = auth_client(sup)
        sup_ac.post(f'{TEAMS_URL}supervisor-requests/{req_id}/respond/', {'action': 'accept'})
        notifs = Notification.objects.filter(recipient=student)
        assert notifs.exists()
        titles = [n.title.lower() for n in notifs]
        assert any('supervisor' in t for t in titles)

    def test_TC5_reject_sends_rejection_notification(self, client, auth_client, make_student, make_supervisor):
        from apps.notifications.models import Notification
        student = make_student()
        sup = make_supervisor()
        team_id, ac = self._create_team(auth_client, student)
        req_res = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': 1})
        req_id = req_res.data['id']
        sup_ac = auth_client(sup)
        respond = sup_ac.post(f'{TEAMS_URL}supervisor-requests/{req_id}/respond/', {'action': 'reject'})
        assert respond.status_code == 200
        assert respond.data['status'] == 'rejected'
        notifs = Notification.objects.filter(recipient=student)
        assert notifs.filter(title__icontains='rejected').exists() or \
               notifs.filter(message__icontains='declined').exists()

    def test_TC5_second_request_stays_pending_after_first_rejects(self, client, auth_client, make_student, make_supervisor):
        student = make_student()
        sup1 = make_supervisor()
        sup2 = make_supervisor()
        team_id, ac = self._create_team(auth_client, student)
        req1 = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup1.id, 'priority': 1})
        ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup2.id, 'priority': 2})
        # sup1 rejects
        sup1_ac = auth_client(sup1)
        sup1_ac.post(f'{TEAMS_URL}supervisor-requests/{req1.data["id"]}/respond/', {'action': 'reject'})
        # sup2's request must still be pending
        reqs = ac.get(f'{TEAMS_URL}{team_id}/supervisor-requests/')
        sup2_req = next(r for r in reqs.data if r['supervisor'] == sup2.id)
        assert sup2_req['status'] == 'pending'

    def test_TC6_all_reject_team_has_no_supervisor(self, client, auth_client, make_student, make_supervisor):
        student = make_student()
        sups = [make_supervisor() for _ in range(3)]
        team_id, ac = self._create_team(auth_client, student)
        req_ids = []
        for i, sup in enumerate(sups):
            r = ac.post(f'{TEAMS_URL}{team_id}/supervisor-request/', {'supervisor_id': sup.id, 'priority': i+1})
            req_ids.append(r.data['id'])
        for sup, req_id in zip(sups, req_ids):
            sup_ac = auth_client(sup)
            sup_ac.post(f'{TEAMS_URL}supervisor-requests/{req_id}/respond/', {'action': 'reject'})
        team_res = ac.get(f'{TEAMS_URL}{team_id}/')
        assert team_res.data['supervisor'] is None
