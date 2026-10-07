from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "app_version" in data
    assert "model_loaded" in data
    assert "device" in data
    assert "artifacts_status" in data
    assert isinstance(data["artifacts_status"], dict)
    assert data["artifacts_status"]["temperature_scaling_exists"] is True
    assert data["artifacts_status"]["decision_threshold_exists"] is True
    assert data["artifacts_status"]["uncertainty_summary_exists"] is True
