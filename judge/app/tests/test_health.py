from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.app_factory import create_app


def test_health_ok_when_worker_alive():
    app = create_app()
    app.router.lifespan_context = None
    task = MagicMock()
    task.done.return_value = False
    app.state.worker_task = task
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_down_when_worker_dead():
    app = create_app()
    app.router.lifespan_context = None
    task = MagicMock()
    task.done.return_value = True
    app.state.worker_task = task
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert response.status_code == 503
