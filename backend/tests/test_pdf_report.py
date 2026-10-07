import uuid
from datetime import datetime
from pathlib import Path
from app.database.session import SessionLocal, init_db
from app.database.models import AnalysisRecord
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_pdf_report_generation():
    init_db()
    db = SessionLocal()
    test_id = str(uuid.uuid4())
    record = AnalysisRecord(
        id=test_id,
        created_at=datetime.utcnow(),
        original_filename="pdf_test.png",
        prediction="NORMAL",
        class_index=0,
        normal_probability=0.92,
        pneumonia_probability=0.08,
        confidence=0.92,
        uncertainty=0.08,
        status="ACCEPTED",
        decision_threshold=0.16,
        uncertainty_threshold=0.10,
        temperature=1.0726476907730103,
        original_image_path="none",
        gradcam_image_path="none"
    )
    db.add(record)
    db.commit()

    # Generate report
    res = client.get(f"/report/{test_id}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000  # PDF generated with content
    assert res.content.startswith(b"%PDF")
