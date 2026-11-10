import pytest
from src.admin import router as admin_router
from src.security.security import security


URL = "/admin/addRole"


def _set_token(client, token):
    client.cookies.set("access_token_cookie", token)


class TestAddRoleAuth:

    def test_add_role_requires_auth(self, client):
        client.cookies.clear()
        response = client.post(URL, params={"uid": 1, "role": "user"})
        assert response.status_code == 401

    def test_add_role_with_invalid_token(self, client):
        _set_token(client, "not-a-jwt")
        try:
            response = client.post(URL, params={"uid": 1, "role": "user"})
        finally:
            client.cookies.clear()
        assert response.status_code == 401

    def test_add_role_without_params_requires_auth_first(self, client):
        client.cookies.clear()
        response = client.post(URL)
        assert response.status_code == 401


class TestAddRoleHappyPath:

    def test_add_role_success_as_admin(self, client, monkeypatch):
        token = security.create_access_token(
            uid="admin-uid", data={"role": "admin"}
        )

        called = {}

        async def fake_add_user_role(uid, role):
            called["uid"] = uid
            called["role"] = role

        monkeypatch.setattr(admin_router, "add_user_role", fake_add_user_role)

        _set_token(client, token)
        try:
            response = client.post(URL, params={"uid": 5, "role": "teacher"})
        finally:
            client.cookies.clear()

        assert response.status_code == 200
        assert called == {"uid": "5", "role": "teacher"}

    def test_add_role_forbidden_for_non_admin(self, client, monkeypatch):
        token = security.create_access_token(
            uid="user-uid", data={"role": "user"}
        )

        called = {"hit": False}

        async def fake_add_user_role(uid, role):
            called["hit"] = True

        monkeypatch.setattr(admin_router, "add_user_role", fake_add_user_role)

        _set_token(client, token)
        try:
            response = client.post(URL, params={"uid": 5, "role": "teacher"})
        finally:
            client.cookies.clear()

        assert response.status_code in (401, 403)
        assert called["hit"] is False