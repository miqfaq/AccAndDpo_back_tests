import pytest
from src.authorisation import router as auth_router



# ============================================================
#  /auth/login
# ============================================================

class TestLogin:
    URL = "/auth/login"
    CREDS = {"login": "alice@example.com", "password": "secret123"}

    def test_login_success(self, client, monkeypatch):
        async def fake_is_verified(login, password):
            return True

        async def fake_get_token(login):
            return "fake.jwt.token"

        monkeypatch.setattr(auth_router, "is_verified", fake_is_verified)
        monkeypatch.setattr(auth_router, "get_token", fake_get_token)

        response = client.post(self.URL, json=self.CREDS)

        assert response.status_code == 200
        assert response.json() == {"access_token": "fake.jwt.token"}
        assert "access_token_cookie" in response.cookies

    def test_login_wrong_password(self, client, monkeypatch):
        async def fake_is_verified(login, password):
            return False

        monkeypatch.setattr(auth_router, "is_verified", fake_is_verified)

        response = client.post(self.URL, json=self.CREDS)

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect login or password"
        assert "access_token_cookie" not in response.cookies

    def test_login_unknown_user(self, client, monkeypatch):
        async def fake_is_verified(login, password):
            return False

        monkeypatch.setattr(auth_router, "is_verified", fake_is_verified)

        response = client.post(
            self.URL, json={"login": "ghost@example.com", "password": "x"}
        )
        assert response.status_code == 401

    @pytest.mark.parametrize("payload", [
        {},
        {"login": "alice@example.com"},          # нет пароля
        {"password": "secret"},                  # нет логина
        {"login": "not-an-email", "password": "x"},  # ← теперь это 422, и это ОК
    ])
    def test_login_validation_errors(self, client, payload):
        response = client.post(self.URL, json=payload)
        assert response.status_code == 422

# ============================================================
#  /auth/register
# ============================================================

class TestRegister:
    URL = "/auth/register"
    NEW_USER = {"login": "bob@example.com", "password": "qwerty123"}

    def test_register_success(self, client, monkeypatch):
        async def fake_register_user(login, password):
            return True

        monkeypatch.setattr(auth_router, "register_user", fake_register_user)

        response = client.post(self.URL, json=self.NEW_USER)

        assert response.status_code == 201
        assert response.json() == "Sucess!"

    def test_register_conflict(self, client, monkeypatch):
        async def fake_register_user(login, password):
            return False

        monkeypatch.setattr(auth_router, "register_user", fake_register_user)

        response = client.post(self.URL, json=self.NEW_USER)

        assert response.status_code == 409
        assert response.json()["detail"] == "Conflict"

    def test_register_passes_creds_to_service(self, client, monkeypatch):
        captured = {}

        async def fake_register_user(login, password):
            captured["login"] = login
            captured["password"] = password
            return True

        monkeypatch.setattr(auth_router, "register_user", fake_register_user)

        client.post(self.URL, json=self.NEW_USER)
        assert captured == {"login": "bob@example.com", "password": "qwerty123"}

    def test_register_missing_password(self, client):
        response = client.post(self.URL, json={"login": "bob@example.com"})
        assert response.status_code == 422

