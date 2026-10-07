import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_validation_missing_model():
    # If model is not loaded, it should return 503 Service Unavailable
    file_content = b"fake image content"
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
    res = client.post("/predict", files=files)
    # Since best_robustness_finetuned_densenet121.pth is pending, should return 503
    assert res.status_code == 503
    assert "standby mode" in res.json()["detail"] or "not found" in res.json()["detail"]
