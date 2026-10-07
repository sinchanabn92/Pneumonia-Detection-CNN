# Pneumonia-AI-System — Clinical Research Prototype

A production-grade, reproducible research prototype web application for pneumonia detection from frontal chest X-ray radiographs (CXR).

This system integrates an existing trained **DenseNet121** model, post-hoc **Temperature Scaling** probability calibration, sensitivity-optimized **Decision Thresholding** ($\tau = 0.16$), confidence-based **Uncertainty Abstention** ($\theta_u = 0.10$), and **DenseBlock4 Grad-CAM** visual interpretability.

> **MANDATORY RESEARCH DISCLAIMER**  
> This application is a research prototype developed strictly for educational and experimental purposes. It is **not** a certified medical diagnostic device and **must not** be used as a substitute for professional evaluation by a licensed radiologist or healthcare provider. Grad-CAM visual heatmaps highlight image features that contributed to model activations; they do not prove pathology or replace clinical diagnosis.

---

## 1. System Architecture

```
                                    +---------------------------+
                                    |     User / Clinician      |
                                    +-------------+-------------+
                                                  |
                                                  v
                                    +---------------------------+
                                    |    React + Vite Frontend  |
                                    |  Tailwind CSS Dashboard   |
                                    +-------------+-------------+
                                                  | REST API (JSON / Multipart)
                                                  v
                                    +---------------------------+
                                    |      FastAPI Backend      |
                                    |  Validation & Pipeline    |
                                    +-------------+-------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                        |                                        |
         v                                        v                                        v
+------------------+                    +--------------------+                   +--------------------+
|  Preprocessing   |                    |   DenseNet121      |                   |    SQLite & PDF    |
|  224x224, Gray,  |                    | Features (Conv)    |                   | Audit History Log  |
|  ImageNet Norm   |                    | Classifier (1024x2)|                   | ReportLab Summary  |
+--------+---------+                    +---------+----------+                   +--------------------+
         |                                        |
         +-----------------> Logits ------------->|
                                                  v
                                        +--------------------+
                                        |    Calibration     |
                                        | Temperature T=1.07 |
                                        +---------+----------+
                                                  | Calibrated Probabilities
                                                  v
                                        +--------------------+
                                        | Decision Threshold |
                                        |  P(Pneumonia)>=0.16|
                                        +---------+----------+
                                                  | Prediction (NORMAL / PNEUMONIA)
                                                  v
                                        +--------------------+
                                        | Uncertainty Check  |
                                        |  (1 - Conf) <= 0.10|
                                        +---------+----------+
                                                  | Status (ACCEPTED / REVIEW)
                                                  v
                                        +--------------------+
                                        | Real Grad-CAM      |
                                        | features.denseblk4 |
                                        +--------------------+
```

---

## 2. Directory Structure

```
Pneumonia-AI-System/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py               # REST API Endpoints (/health, /model-info, /predict, etc.)
│   │   │   └── schemas.py              # Pydantic V2 Request & Response schemas
│   │   ├── database/
│   │   │   ├── models.py               # SQLAlchemy AnalysisRecord schema
│   │   │   └── session.py              # SQLite engine and session factory
│   │   ├── model/
│   │   │   ├── densenet.py             # 100% matched native DenseNet121 architecture
│   │   │   ├── loader.py               # Single startup model loader & validator
│   │   │   ├── preprocessing.py        # Resize, Grayscale(3), ToTensor, ImageNet Norm
│   │   │   ├── calibration.py          # Temperature scaling (T = 1.0726476907730103)
│   │   │   ├── uncertainty.py          # Decision threshold (0.16) & Abstention (0.10)
│   │   │   ├── gradcam.py              # Real DenseBlock4 Grad-CAM hooks and overlay generator
│   │   │   └── inference.py            # Unified end-to-end inference orchestrator
│   │   ├── services/
│   │   │   └── report_service.py       # Dynamic ReportLab clinical PDF generator
│   │   ├── config.py                   # Pydantic Settings & environment constants
│   │   └── main.py                     # FastAPI application entry point
│   ├── artifacts/                      # Deployment configuration artifacts
│   │   ├── model/
│   │   │   └── best_robustness_finetuned_densenet121.pth (Trained checkpoint)
│   │   ├── calibration/
│   │   │   └── temperature_scaling.json
│   │   ├── decision/
│   │   │   └── selected_decision_threshold.json
│   │   ├── uncertainty/
│   │   │   └── uncertainty_summary.json
│   │   ├── gradcam/
│   │   │   └── gradcam_methodology.json
│   │   └── preprocessing/
│   │       └── training_configuration.csv
│   ├── storage/                        # Generated runtime data (SQLite, uploads, overlays)
│   ├── tests/                          # Pytest automated test suite (8 tests)
│   └── requirements.txt                # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                 # Navbar, Footer, Status indicators
│   │   ├── pages/                      # Dashboard, Upload, Results, History, Model Specs
│   │   ├── api.js                      # Axios API client
│   │   ├── App.jsx                     # Root router & layout
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── notebooks/                          # Source of Truth Research Notebooks
│   ├── model_training_on_CXR_dataset.ipynb
│   ├── external_testing_results_on_keranmaye_dataset.ipynb
│   └── Untitled3_(1).ipynb
└── README.md
```

---

## 3. Machine Learning Configuration (Source of Truth)

### 3.1 Model & Classifier
- **Architecture**: DenseNet121 (`torchvision.models.densenet121` equivalent).
- **Feature Extractor**: 4 Dense Blocks with transition layers (727 parameter tensors).
- **Classifier**: `nn.Linear(in_features=1024, out_features=2, bias=True)`.
- **Target Checkpoint**: `best_robustness_finetuned_densenet121.pth`.
- **Class Indices**: `0 = NORMAL`, `1 = PNEUMONIA`.
- **Zero Runtime Training**: The deployed backend strictly performs evaluation (`model.eval()`). Weights are never modified.

### 3.2 Exact Input Preprocessing
1. **Resize**: Resized to $224 \times 224$ pixels using bilinear interpolation.
2. **Grayscale**: Converted to single-channel luminance, then repeated across 3 channels.
3. **ToTensor**: Scaled to float tensors in range $[0.0, 1.0]$.
4. **ImageNet Normalization**:
   - Mean: `[0.485, 0.456, 0.406]`
   - Standard Deviation: `[0.229, 0.224, 0.225]`
5. **No Inference Augmentation**: Uploaded radiographs are never rotated, jittered, blurred, or cropped at inference time.

### 3.3 Post-Hoc Temperature Scaling
- **Temperature Parameter**: $T = 1.0726476907730103$ (read from `temperature_scaling.json`).
- **Calculation**:
  $$\mathbf{z}_{\text{scaled}} = \frac{\mathbf{z}}{T}, \quad \mathbf{p} = \text{softmax}(\mathbf{z}_{\text{scaled}})$$
- **Effect**: Reduces calibration error (ECE improves from 0.0063 to 0.0036) without changing accuracy or classification rank.

### 3.4 Decision Threshold Optimization
- **Threshold**: $\tau = 0.16$ for Pneumonia posterior probability (read from `selected_decision_threshold.json`).
- **Decision Rule**:
  $$\hat{y} = \begin{cases} \text{PNEUMONIA}, & \text{if } P(\text{Pneumonia}) \ge 0.16 \\ \text{NORMAL}, & \text{otherwise} \end{cases}$$
- **Clinical Rationale**: At the standard 0.50 cutoff, false negatives are elevated. Selecting $\tau = 0.16$ achieves **98.16% sensitivity** while maintaining $\ge 95\%$ specificity on validation splits.

### 3.5 Uncertainty & Confidence-Based Abstention
- **Confidence**: $C = P(\hat{y}) = \max(P(\text{Normal}), P(\text{Pneumonia}))$.
- **Uncertainty**: $U = 1 - C$.
- **Abstention Cutoff**: $\theta_u = 0.10$ (read from `uncertainty_summary.json`).
- **Status Assignment**:
  $$\text{Status} = \begin{cases} \text{ACCEPTED}, & \text{if } U \le 0.10 \\ \text{UNCERTAIN / REVIEW}, & \text{if } U > 0.10 \end{cases}$$
- **Design Principle**: The class prediction remains either `NORMAL` or `PNEUMONIA`; uncertainty is tracked separately to guide human-in-the-loop review.

### 3.6 Explainability (Grad-CAM on DenseBlock4)
- **Target Module**: `model.features.denseblock4` (final convolutional representation before pooling).
- **Execution Mode**: Runs with gradients enabled (`torch.set_grad_enabled(True)`).
- **Gradient Weights**: Global average pooling over spatial dimensions:
  $$\alpha_k^c = \frac{1}{H \times W} \sum_{i=1}^H \sum_{j=1}^W \frac{\partial Y^c}{\partial A_{i,j}^k}$$
- **Visualization**: Linear combination with ReLU activation, normalized to $[0, 1]$, colormapped with `jet`, and blended at $\alpha = 0.45$ over the grayscale radiograph.

---

## 4. Ground Truth Evaluation Metrics

| Benchmark Dataset | Samples | Accuracy | Precision | Sensitivity | Specificity | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Internal Test Split** (Clean CXR) | 5,439 | **96.38%** | 94.78% | **98.16%** | 94.60% | 96.44% | 0.9960 |
| **Kermany Pediatric** (External Zero-Shot) | 624 | **95.35%** | 93.08% | **100.00%** | 87.61% | 96.42% | 0.9998 |

*Data directly verified from Notebook 3 experiments (`internal_vs_external_generalization.csv` and `final_test_results.json`).*

---

## 5. Setup & Running Instructions

### 5.1 Prerequisites
- Python 3.11 (`python.exe`)
- Node.js v18+ and npm (`node`, `npm`)

### 5.2 Backend Setup
1. Open a terminal in `backend/`:
   ```bash
   cd Pneumonia-AI-System/backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the automated test suite:
   ```bash
   pytest tests/ -v
   ```
4. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The interactive Swagger documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 5.3 Frontend Setup
1. Open a terminal in `frontend/`:
   ```bash
   cd Pneumonia-AI-System/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   The web application will open at [http://localhost:5173](http://localhost:5173).

---

## 6. Model Checkpoint Deployment Instructions

To connect your trained checkpoint:
1. Place the checkpoint file into:
   ```
   backend/artifacts/model/best_robustness_finetuned_densenet121.pth
   ```
2. Restart or reload the FastAPI backend.
3. Verify `/health` reports:
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "device": "cpu"
   }
   ```
4. Perform uploads on the frontend to execute real end-to-end inference and Grad-CAM generation.

---

## 7. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Application health, model readiness, device, and artifact status. |
| `GET` | `/model-info` | Complete architectural, calibration, threshold, and benchmark specs. |
| `POST` | `/predict` | Multipart upload of CXR image; returns prediction, probabilities, uncertainty, and Grad-CAM URL. |
| `GET` | `/history` | Paginated list of historical analyses stored in SQLite. |
| `GET` | `/history/{id}` | Detailed record of a specific analysis. |
| `GET` | `/report/{id}` | Dynamically streams a ReportLab clinical summary PDF report. |
| `GET` | `/static/*` | Static file serving for uploads and generated Grad-CAM overlays. |
