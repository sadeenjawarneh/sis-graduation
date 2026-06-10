import pytest

from apps.activity.models import ActivityLog
from apps.teams.models import Team


@pytest.mark.django_db
def test_admin_can_add_and_remove_student_from_team(auth_client, make_admin, make_student, make_team):
    admin = make_admin()
    leader = make_student()
    student = make_student()
    team = make_team(leader=leader)
    ac = auth_client(admin)

    add_res = ac.post(f'/api/teams/{team.id}/students/', {'student_id': student.id})

    assert add_res.status_code == 200
    team.refresh_from_db()
    assert team.members.filter(pk=student.pk).exists()

    remove_res = ac.delete(f'/api/teams/{team.id}/students/{student.id}/')

    assert remove_res.status_code == 200
    team.refresh_from_db()
    assert not team.members.filter(pk=student.pk).exists()
    assert ActivityLog.objects.filter(action='Student Removed From Team').exists()


@pytest.mark.django_db
def test_admin_can_assign_or_clear_team_supervisor(auth_client, make_admin, make_student, make_supervisor, make_team):
    admin = make_admin()
    leader = make_student()
    supervisor = make_supervisor()
    team = make_team(leader=leader)
    ac = auth_client(admin)

    assign_res = ac.post(f'/api/teams/{team.id}/supervisor/', {'supervisor_id': supervisor.id})

    assert assign_res.status_code == 200
    team.refresh_from_db()
    assert team.assigned_supervisor_id == supervisor.id

    clear_res = ac.post(f'/api/teams/{team.id}/supervisor/', {'supervisor_id': None}, format='json')

    assert clear_res.status_code == 200
    team.refresh_from_db()
    assert team.assigned_supervisor_id is None


@pytest.mark.django_db
def test_auto_merge_preview_groups_unassigned_students(auth_client, make_admin, make_student):
    admin = make_admin()
    for index in range(7):
        make_student(email=f'unassigned{index}@cit.just.edu.jo')
    ac = auth_client(admin)

    res = ac.get('/api/auto-merge/preview/')

    assert res.status_code == 200
    preview = res.data['preview']
    assert preview['unassigned_students_count'] == 7
    assert sorted(team['size'] for team in preview['teams_to_create']) == [3, 4]
    assert all(not team['unavoidable_under_minimum'] for team in preview['teams_to_create'])


@pytest.mark.django_db
def test_auto_merge_run_creates_teams_and_balances_supervisors(auth_client, make_admin, make_student, make_supervisor, make_team):
    admin = make_admin()
    supervisor_a = make_supervisor(display_name='A Supervisor')
    supervisor_b = make_supervisor(display_name='B Supervisor')
    existing_leader = make_student(email='leader@cit.just.edu.jo')
    make_team(leader=existing_leader, supervisor=supervisor_a)
    unassigned_team = make_team(leader=make_student(email='unassigned-team-leader@cit.just.edu.jo'), supervisor=None)
    for index in range(6):
        make_student(email=f'auto{index}@cit.just.edu.jo')
    ac = auth_client(admin)

    res = ac.post('/api/auto-merge/run/')

    assert res.status_code == 200
    assert res.data['created_teams_count'] == 2
    assert res.data['assigned_teams_count'] >= 1
    assert Team.objects.filter(name__startswith='Auto Team').count() == 2
    unassigned_team.refresh_from_db()
    assert unassigned_team.assigned_supervisor_id == supervisor_b.id
    assert ActivityLog.objects.filter(action='Auto Merge Team Created').count() == 2
