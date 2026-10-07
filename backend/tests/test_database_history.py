import uuid
from datetime import datetime
from app.database.session import SessionLocal, init_db
from app.database.models import AnalysisRecord
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_database_and_history():
    init_db()
    db = SessionLocal()
    
    test_id = str(uuid.uuid4())
    record = AnalysisRecord(
        id=test_id,
        created_at=datetime.utcnow(),
        original_filename="test_xray.png",
        prediction="PNEUMONIA",
        class_index=1,
        normal_probability=0.04,
        pneumonia_probability=0.96,
        confidence=0.96,
        uncertainty=0.04,
        status="ACCEPTED",
        decision_threshold=0.16,
        uncertainty_threshold=0.10,
        temperature=1.0726476907730103,
        original_image_path="test_orig.png",
        gradcam_image_path="test_cam.png"
    )
    db.add(record)
    db.commit()

    # Query via API
    res = client.get("/history")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    
    # Query single item
    res_single = client.get(f"/history/{test_id}")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["analysis_id"] == test_id
    assert single_data["prediction"] == "PNEUMONIA"
    assert single_data["confidence"] == 0.96
    assert single_data["status"] == "ACCEPTED"

    # Non-existent ID returns 404
    res_404 = client.get(f"/history/non-existent-uuid")
    assert res_404.status_code == 404
