from fastapi.testclient import TestClient

from app.main import app


def test_raiz():
    assert TestClient(app).get("/").status_code == 200