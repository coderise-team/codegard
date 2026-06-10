from fastapi.testclient import TestClient
from app.app_factory import create_app


def test_health():
    app = create_app()
    app.router.lifespan_context = None
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
