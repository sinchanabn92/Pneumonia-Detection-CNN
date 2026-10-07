from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime
from app.database.session import Base

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    original_filename = Column(String(255), nullable=False)
    prediction = Column(String(32), nullable=False)
    class_index = Column(Integer, nullable=False)
    normal_probability = Column(Float, nullable=False)
    pneumonia_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    status = Column(String(64), nullable=False)
    decision_threshold = Column(Float, nullable=False)
    uncertainty_threshold = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    original_image_path = Column(String(512), nullable=False)
    gradcam_image_path = Column(String(512), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "original_filename": self.original_filename,
            "prediction": self.prediction,
            "class_index": self.class_index,
            "normal_probability": round(self.normal_probability, 4),
            "pneumonia_probability": round(self.pneumonia_probability, 4),
            "confidence": round(self.confidence, 4),
            "uncertainty": round(self.uncertainty, 4),
            "status": self.status,
            "decision_threshold": self.decision_threshold,
            "uncertainty_threshold": self.uncertainty_threshold,
            "temperature": self.temperature,
            "original_image_url": f"/static/uploads/{self.id}_{self.original_filename}",
            "gradcam_url": f"/static/gradcam/gradcam_{self.id}.png"
        }
