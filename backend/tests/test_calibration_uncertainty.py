import torch
from app.model.calibration import TemperatureScaler
from app.model.uncertainty import DecisionAndUncertaintyEvaluator

def test_temperature_scaling():
    scaler = TemperatureScaler()
    assert abs(scaler.temperature - 1.0726476907730103) < 1e-4

    # Dummy logits
    logits = torch.tensor([[2.0, 1.0]])
    probs = scaler.scale_and_softmax(logits)
    assert probs.shape == (1, 2)
    assert abs(probs.sum().item() - 1.0) < 1e-5
    # High logit for class 0 means class 0 prob > class 1 prob
    assert probs[0, 0] > probs[0, 1]

def test_decision_threshold_and_uncertainty():
    evaluator = DecisionAndUncertaintyEvaluator()
    assert abs(evaluator.decision_threshold - 0.16) < 0.01
    assert abs(evaluator.uncertainty_threshold - 0.10) < 0.01

    # Case 1: Pneumonia probability >= 0.16 -> PNEUMONIA
    # Pneumonia prob = 0.95 (uncertainty = 1 - 0.95 = 0.05 <= 0.10 -> ACCEPTED)
    res1 = evaluator.evaluate(normal_prob=0.05, pneumonia_prob=0.95)
    assert res1["prediction"] == "PNEUMONIA"
    assert res1["class_index"] == 1
    assert res1["confidence"] == 0.95
    assert res1["uncertainty"] == 0.05
    assert res1["status"] == "ACCEPTED"

    # Case 2: Pneumonia prob = 0.20 (>= 0.16 -> PNEUMONIA, but uncertainty = 1 - 0.20 = 0.80 > 0.10 -> UNCERTAIN / REVIEW)
    res2 = evaluator.evaluate(normal_prob=0.80, pneumonia_prob=0.20)
    assert res2["prediction"] == "PNEUMONIA"
    assert res2["class_index"] == 1
    assert res2["confidence"] == 0.20
    assert res2["uncertainty"] == 0.80
    assert res2["status"] == "UNCERTAIN / REVIEW"

    # Case 3: Pneumonia prob = 0.10 (< 0.16 -> NORMAL, normal_prob = 0.90, uncertainty = 0.10 <= 0.10 -> ACCEPTED)
    res3 = evaluator.evaluate(normal_prob=0.90, pneumonia_prob=0.10)
    assert res3["prediction"] == "NORMAL"
    assert res3["class_index"] == 0
    assert res3["confidence"] == 0.90
    assert res3["uncertainty"] == 0.10
    assert res3["status"] == "ACCEPTED"

    # Case 4: Near 0.16 boundary
    # Pneumonia prob = 0.159 -> NORMAL
    res4 = evaluator.evaluate(normal_prob=0.841, pneumonia_prob=0.159)
    assert res4["prediction"] == "NORMAL"
    # Pneumonia prob = 0.160 -> PNEUMONIA
    res5 = evaluator.evaluate(normal_prob=0.840, pneumonia_prob=0.160)
    assert res5["prediction"] == "PNEUMONIA"
