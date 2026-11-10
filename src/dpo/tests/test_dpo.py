from types import SimpleNamespace
from fastapi.testclient import TestClient
from main import app
from src.profile import router as dpo_router
import uuid


URL = "/dpo/{user_id}/latest"


def make_userinfo(**overrides):
    """Простой объект-заглушка вместо ORM-модели пользователя."""
    defaults = {
        "lastName": "Kornilov",
        "firstName": "Alexey",
        "midName": "Dmitrievich",
        "department": "Dev-dep",
        "position": "Middle",
        "area": "Backend",
        "target_role": "Senior",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ============================================================
#  Успешный сценарий
# ============================================================

class TestGetContractSuccess:

    def test_returns_contract_when_user_exists(self, client, monkeypatch):
        user_data = {"uid": "4003709b-1f85-4e40-a7fd-f7c69b6883e4"}
        client = TestClient(app=app)
        response = client.get(f'/dpo/{user_data["uid"]}/latest')
        assert response.status_code == 200
        assert response.json is not None
        

    def test_contract_fail_if_user_not_exist(self, client, monkeypatch):
        uid = str(uuid.uuid4())
        user_data = {"uid": uid}
        client = TestClient(app=app)
        response = client.get(f'/dpo/{user_data["uid"]}/latest')
        assert response.status_code == 204
        assert response.json is not None
        


class TestGetContractRouting:

    def test_wrong_method_returns_405(self, client):
        """POST на GET-ручку — метод не разрешён."""
        response = client.post(URL.format(user_id="4003709b-1f85-4e40-a7fd-f7c69b6883e4"))
        assert response.status_code == 405

    def test_trailing_segment_required(self, client):
        """Без /latest — 404 (эндпоинт не совпадает)."""
        response = client.get("/dpo/u1")
        assert response.status_code == 404