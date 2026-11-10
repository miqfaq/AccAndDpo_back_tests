import pytest
from fastapi.testclient import TestClient
from main import app  # у вас main.py в корне, там app = FastAPI()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()