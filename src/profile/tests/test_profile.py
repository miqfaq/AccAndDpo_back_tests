import json
import pytest
from types import SimpleNamespace

from src.profile import router as profile_router
from src.security.security import security


def make_token(uid="user-uid", role="user"):
    return security.create_access_token(uid=uid, data={"role": role})


def auth_headers(uid="user-uid", role="user"):
    """Заголовок Authorization — ручки используют access_token_required."""
    return {"Authorization": f"Bearer {make_token(uid, role)}"}


# ============================================================
#  GET /profile/getuserinfo
# ============================================================

class TestGetUserInfo:

    URL = "/profile/getuserinfo"

    def test_requires_auth(self, client):
        client.cookies.clear()
        response = client.get(self.URL)
        assert response.status_code == 401

    def test_returns_user_data(self, client, monkeypatch):
        async def fake_find_user_uid(uid):
            return True

        async def fake_get_user_data(uid):
            return {"uid": uid, "lastName": "Kornilov", "firstName": "Alexey"}

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "get_user_data", fake_get_user_data)
        auth_res = client.get("/login")
        auth_token = auth_res.json["access_token"]
        response = client.get(self.URL, headers=auth_token)

        assert response.status_code == 200
        assert response.json()["uid"] == "4003709b-1f85-4e40-a7fd-f7c69b6883e4"
        assert response.json()["lastName"] == "Kornilov"

    def test_uses_sub_from_token(self, client, monkeypatch):
        """uid берётся из payload.sub, а не из параметров запроса."""
        captured = {}

        async def fake_find_user_uid(uid):
            captured["find"] = uid
            return True

        async def fake_get_user_data(uid):
            captured["get"] = uid
            return {}

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "get_user_data", fake_get_user_data)

        client.get(self.URL, headers=auth_headers("subject-42"))

        assert captured == {"find": "subject-42", "get": "subject-42"}

    def test_returns_204_when_user_missing(self, client, monkeypatch):
        async def fake_find_user_uid(uid):
            return False

        async def fake_get_user_data(uid):
            raise AssertionError("get_user_data не должен вызываться")

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "get_user_data", fake_get_user_data)

        response = client.get(self.URL, headers=auth_headers())

        assert response.status_code == 204


# ============================================================
#  PATCH /profile/updateUser
# ============================================================

class TestUpdateUser:

    URL = "/profile/updateUser"
    BODY = {"lastName": "New", "firstName": "Name"}

    def test_requires_auth(self, client):
        client.cookies.clear()
        response = client.patch(self.URL, json=self.BODY)
        assert response.status_code == 401

    def test_updates_user_data(self, client, monkeypatch):
        captured = {}

        async def fake_find_user_uid(uid):
            return True

        async def fake_update_user_data(userjson, uid):
            captured["payload"] = userjson
            captured["uid"] = uid

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "update_user_data", fake_update_user_data)

        response = client.patch(
            self.URL, json=self.BODY, headers=auth_headers("u1")
        )

        assert response.status_code == 200
        assert captured["uid"] == "u1"
        assert captured["payload"].lastName == "New"
        assert captured["payload"].firstName == "Name"

    def test_returns_204_when_user_missing(self, client, monkeypatch):
        async def fake_find_user_uid(uid):
            return False

        async def fake_update_user_data(userjson, uid):
            raise AssertionError("update_user_data не должен вызываться")

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "update_user_data", fake_update_user_data)

        response = client.patch(
            self.URL, json=self.BODY, headers=auth_headers()
        )
        assert response.status_code == 204

    def test_invalid_body_returns_422(self, client):
        """UserDataOut валидируется FastAPI до входа в ручку."""
        response = client.patch(
            self.URL, json={"unknown_field": 1}, headers=auth_headers()
        )
        assert response.status_code == 422


# ============================================================
#  DELETE /profile/deleteUser
# ============================================================

class TestDeleteUser:

    URL = "/profile/deleteUser"

    def test_requires_auth(self, client):
        client.cookies.clear()
        response = client.delete(self.URL)
        assert response.status_code == 401

    def test_deletes_user(self, client, monkeypatch):
        captured = {}

        async def fake_find_user_uid(uid):
            return True

        async def fake_delete_user_data(uid):
            captured["uid"] = uid

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "delete_user_data", fake_delete_user_data)

        response = client.delete(self.URL, headers=auth_headers("u1"))

        assert response.status_code == 200
        assert captured["uid"] == "u1"

    def test_returns_204_when_user_missing(self, client, monkeypatch):
        async def fake_find_user_uid(uid):
            return False

        async def fake_delete_user_data(uid):
            raise AssertionError("delete_user_data не должен вызываться")

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "delete_user_data", fake_delete_user_data)

        response = client.delete(self.URL, headers=auth_headers())
        assert response.status_code == 204


# ============================================================
#  POST /profile/addAcc
# ============================================================

class TestAddAccreditation:

    URL = "/profile/addAcc"
    BODY = {"uid": "acc-1", "target": 50, "rating": 20,
            "direction": "BACKEND", "skill": "PYTHON", "self_rating": 5}

    def test_requires_auth(self, client):
        client.cookies.clear()
        response = client.post(self.URL, json=self.BODY)
        assert response.status_code == 401

    def test_adds_accreditation(self, client, monkeypatch):
        captured = {}

        async def fake_find_user_uid(uid):
            return True

        async def fake_add_accreditation(acc, uid):
            captured["acc"] = acc
            captured["uid"] = uid

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "add_accreditation", fake_add_accreditation)

        response = client.post(
            self.URL, json=self.BODY, headers=auth_headers("u1")
        )

        assert response.status_code == 200
        assert response.json() == "sucess"   # опечатка в контракте — фиксируем
        assert captured["uid"] == "u1"
        assert captured["acc"].skill == "PYTHON"

    def test_returns_204_when_user_missing(self, client, monkeypatch):
        async def fake_find_user_uid(uid):
            return False

        async def fake_add_accreditation(acc, uid):
            raise AssertionError("add_accreditation не должен вызываться")

        monkeypatch.setattr(profile_router, "find_user_uid", fake_find_user_uid)
        monkeypatch.setattr(profile_router, "add_accreditation", fake_add_accreditation)

        response = client.post(
            self.URL, json=self.BODY, headers=auth_headers()
        )
        assert response.status_code == 204

    def test_invalid_body_returns_422(self, client):
        response = client.post(
            self.URL, json={"skill": "PYTHON"}, headers=auth_headers()
        )
        assert response.status_code == 422


# ============================================================
#  GET /profile/getAccType
# ============================================================

class TestGetAccType:

    URL = "/profile/getAccType"

    def test_requires_auth(self, client):
        """Роутер висит на dependencies=[...], значит и эта ручка защищена."""
        client.cookies.clear()
        response = client.get(self.URL)
        assert response.status_code == 401

    def test_returns_competencies_from_cache(self, client, monkeypatch, tmp_path):
        cache_file = tmp_path / "local_cache.json"
        cache_file.write_text(
            json.dumps({"competencies": ["PYTHON", "SQL", "GO"]}),
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)   # ручка открывает "local_cache.json" относительно cwd

        response = client.get(self.URL, headers=auth_headers())

        assert response.status_code == 200
        assert response.json() == ["PYTHON", "SQL", "GO"]

    def test_returns_500_when_cache_missing(self, client, monkeypatch, tmp_path):
        """Если файла нет — ручка упадёт с FileNotFoundError → 500."""
        monkeypatch.chdir(tmp_path)   # пустая директория, файла нет

        response = client.get(self.URL, headers=auth_headers())

        assert response.status_code == 500