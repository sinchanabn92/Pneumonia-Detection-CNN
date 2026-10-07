from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_model_info_endpoint():
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Robustness-improved DenseNet121"
    assert data["target_layer"] == "features.denseblock4"
    assert data["input_size"] == "224 × 224"
    assert data["classes"] == {"0": "NORMAL", "1": "PNEUMONIA"}
    assert round(data["temperature"], 4) == round(1.0726476907730103, 4)
    assert round(data["decision_threshold"], 2) == 0.16
    assert data["uncertainty_threshold"] == 0.10
    assert "internal_test_metrics" in data
    assert data["internal_test_metrics"]["accuracy"] == 0.9638
    assert "external_test_metrics" in data
    assert data["external_test_metrics"]["accuracy"] == 0.9535
    assert "disclaimer" in data
