"""
Grading Tests — mirrors grading.cy.js
TC-1  Three grades → correct final (50/25/25)
TC-2  Boundary: 0 and 100 accepted, -1 and 101 rejected
TC-3  Weight distribution verified
TC-4  Missing grade → 400
"""
import pytest
from decimal import Decimal

PREVIEW_URL = '/api/v1/grading/preview/'


@pytest.mark.django_db
class TestGradePreview:

    def test_TC1_correct_final_grade(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        # 80*0.5 + 70*0.25 + 60*0.25 = 40 + 17.5 + 15 = 72.5
        res = ac.post(PREVIEW_URL, {'chief_grade': 80, 'examiner_one_grade': 70, 'examiner_two_grade': 60})
        assert res.status_code == 200
        assert float(res.data['final_grade']) == 72.5

    def test_TC2_all_zero_returns_zero(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 0, 'examiner_one_grade': 0, 'examiner_two_grade': 0})
        assert res.status_code == 200
        assert float(res.data['final_grade']) == 0.0

    def test_TC2_all_hundred_returns_hundred(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 100, 'examiner_one_grade': 100, 'examiner_two_grade': 100})
        assert res.status_code == 200
        assert float(res.data['final_grade']) == 100.0

    def test_TC2_negative_grade_rejected(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': -1, 'examiner_one_grade': 50, 'examiner_two_grade': 50})
        assert res.status_code == 400

    def test_TC2_above_100_rejected(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 101, 'examiner_one_grade': 50, 'examiner_two_grade': 50})
        assert res.status_code == 400

    def test_TC3_chief_only_gives_50_percent(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 100, 'examiner_one_grade': 0, 'examiner_two_grade': 0})
        assert float(res.data['final_grade']) == 50.0

    def test_TC3_examiner1_only_gives_25_percent(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 0, 'examiner_one_grade': 100, 'examiner_two_grade': 0})
        assert float(res.data['final_grade']) == 25.0

    def test_TC3_examiner2_only_gives_25_percent(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 0, 'examiner_one_grade': 0, 'examiner_two_grade': 100})
        assert float(res.data['final_grade']) == 25.0

    def test_TC3_equal_grades_return_same_value(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 60, 'examiner_one_grade': 60, 'examiner_two_grade': 60})
        assert float(res.data['final_grade']) == 60.0

    def test_TC4_missing_chief_grade_returns_400(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'examiner_one_grade': 70, 'examiner_two_grade': 60})
        assert res.status_code == 400

    def test_TC4_missing_examiner1_returns_400(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 80, 'examiner_two_grade': 60})
        assert res.status_code == 400

    def test_TC4_missing_examiner2_returns_400(self, client, auth_client, make_supervisor):
        sup = make_supervisor()
        ac = auth_client(sup)
        res = ac.post(PREVIEW_URL, {'chief_grade': 80, 'examiner_one_grade': 70})
        assert res.status_code == 400

    def test_unauthenticated_request_rejected(self, client):
        res = client.post(PREVIEW_URL, {'chief_grade': 80, 'examiner_one_grade': 70, 'examiner_two_grade': 60})
        assert res.status_code == 401
