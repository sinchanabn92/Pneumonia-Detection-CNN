# Model Checkpoint Directory

Place the trained deployment checkpoint file in this directory:

- File: `best_robustness_finetuned_densenet121.pth`
- Path: `backend/artifacts/model/best_robustness_finetuned_densenet121.pth`

When this file is present, the FastAPI server automatically loads it once at startup and serves real DenseNet121 inference and Grad-CAM interpretability.
If absent, the system starts in safe standby mode, reporting model status via `/health`.
