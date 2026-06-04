"""
Login Tests — mirrors login.cy.js
TC-1  Student valid credentials   → 200 + tokens
TC-2  Invalid email AND password  → 401
TC-3  Valid email / wrong pass    → 401
TC-4  Wrong email / valid pass    → 401
TC-5  Empty email                 → 401
TC-6  Empty password              → 401
TC-7  Supervisor valid creds      → 200 + role=supervisor
TC-8  Supervisor invalid creds    → 401
TC-9  Supervisor wrong password   → 401
TC-10 Supervisor wrong email      → 401
TC-11 Supervisor empty email      → 401
TC-12 Supervisor empty password   → 401
TC-13 Case-insensitive email      → 200 (Django iexact lookup)
"""
import pytest

LOGIN_URL = '/api/v1/auth/login/'


@pytest.mark.django_db
class TestStudentLogin:

    def test_TC1_valid_credentials_returns_tokens(self, client, make_student):
        student = make_student(email='sadeen@cit.just.edu.jo', password='Sadeen0*')
        res = client.post(LOGIN_URL, {'email': 'sadeen@cit.just.edu.jo', 'password': 'Sadeen0*'})
        assert res.status_code == 200
        assert 'access' in res.data
        assert 'refresh' in res.data
        assert res.data['user']['role'] == 'student'

    def test_TC2_invalid_email_and_password(self, client, make_student):
        make_student()
        res = client.post(LOGIN_URL, {'email': 'notexist@just.edu.jo', 'password': 'Wrong123!'})
        assert res.status_code == 401

    def test_TC3_valid_email_wrong_password(self, client, make_student):
        student = make_student(email='sadeen@cit.just.edu.jo', password='Sadeen0*')
        res = client.post(LOGIN_URL, {'email': 'sadeen@cit.just.edu.jo', 'password': 'WrongPass999!'})
        assert res.status_code == 401

    def test_TC4_wrong_email_valid_password(self, client, make_student):
        make_student(email='sadeen@cit.just.edu.jo', password='Sadeen0*')
        res = client.post(LOGIN_URL, {'email': 'notexist@just.edu.jo', 'password': 'Sadeen0*'})
        assert res.status_code == 401

    def test_TC5_empty_email_returns_401(self, client, make_student):
        make_student()
        res = client.post(LOGIN_URL, {'email': '', 'password': 'Sadeen0*'})
        assert res.status_code == 401

    def test_TC6_empty_password_returns_401(self, client, make_student):
        student = make_student(email='sadeen@cit.just.edu.jo', password='Sadeen0*')
        res = client.post(LOGIN_URL, {'email': 'sadeen@cit.just.edu.jo', 'password': ''})
        assert res.status_code == 401


@pytest.mark.django_db
class TestSupervisorLogin:

    def test_TC7_valid_credentials_returns_supervisor_role(self, client, make_supervisor):
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        res = client.post(LOGIN_URL, {'email': 'Hamza@just.edu.jo', 'password': 'Hamza0*'})
        assert res.status_code == 200
        assert res.data['user']['role'] == 'supervisor'

    def test_TC8_invalid_credentials(self, client, make_supervisor):
        make_supervisor()
        res = client.post(LOGIN_URL, {'email': 'notexist@just.edu.jo', 'password': 'Wrong123!'})
        assert res.status_code == 401

    def test_TC9_valid_email_wrong_password(self, client, make_supervisor):
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        res = client.post(LOGIN_URL, {'email': 'Hamza@just.edu.jo', 'password': 'WrongPass999!'})
        assert res.status_code == 401

    def test_TC10_wrong_email_valid_password(self, client, make_supervisor):
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        res = client.post(LOGIN_URL, {'email': 'notexist@just.edu.jo', 'password': 'Hamza0*'})
        assert res.status_code == 401

    def test_TC11_empty_email(self, client, make_supervisor):
        make_supervisor()
        res = client.post(LOGIN_URL, {'email': '', 'password': 'Hamza0*'})
        assert res.status_code == 401

    def test_TC12_empty_password(self, client, make_supervisor):
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        res = client.post(LOGIN_URL, {'email': 'Hamza@just.edu.jo', 'password': ''})
        assert res.status_code == 401

    def test_TC13_case_insensitive_email_login(self, client, make_supervisor):
        """Login view uses email__iexact so any case should work."""
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        res = client.post(LOGIN_URL, {'email': 'hamza@just.edu.jo', 'password': 'Hamza0*'})
        assert res.status_code == 200


@pytest.mark.django_db
class TestAccountLockout:
    """
    TC-13 Security — Account Lockout
    The login view itself doesn't implement lockout (it's frontend-side in login.html).
    This test verifies the backend always returns 401 for wrong credentials
    regardless of attempt count (lockout is enforced by the UI).
    """

    def test_TC13_repeated_wrong_password_stays_401(self, client, make_supervisor):
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        for _ in range(5):
            res = client.post(LOGIN_URL, {'email': 'Hamza@just.edu.jo', 'password': 'WrongPass!'})
            assert res.status_code == 401

    def test_TC13_correct_password_still_works_after_wrong_attempts(self, client, make_supervisor):
        """Backend does not lock accounts — lockout is frontend-only."""
        make_supervisor(email='Hamza@just.edu.jo', password='Hamza0*')
        for _ in range(5):
            client.post(LOGIN_URL, {'email': 'Hamza@just.edu.jo', 'password': 'WrongPass!'})
        res = client.post(LOGIN_URL, {'email': 'Hamza@just.edu.jo', 'password': 'Hamza0*'})
        assert res.status_code == 200
