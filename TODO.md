# Medicinal Plant Model Training Pipeline
Status: In Progress

## Approved Plan Steps

### 1. Dataset Preparation
- [x] Download & merge script created
- [RUNNING ] python ml_pipeline/download_and_merge.py (3GB datasets)

### 2. Notebook Creation
- [ ] Create `ml_pipeline/medicinal_plant_training.ipynb`
  * Imports first cell
  * Merge dataset code cell
  * Data exploration/visualization
  * Data generators
  * Model definition
  * Phase 1 training (feature extraction)
  * Phase 2 fine-tuning
  * Evaluation & plots
  * Save .h5, TFLite, class_names.json to `ml_pipeline/models/`

### 3. Training Execution
- [ ] Execute notebook
- [ ] Monitor training (GPU usage, accuracy progress)

### 4. Backend Integration
- [ ] Copy models to `backend/ml_models/medicinal_plant_model_v2.h5`
- [ ] Update `backend/app/services/ml_service.py` to load new model
- [ ] Update `backend/ml_models/class_names.json`

### 5. Testing & Validation
- [ ] Test prediction API `/api/v1/predict`
- [ ] Test with sample images from merged dataset
- [ ] Verify accuracies (top-1, top-3)
- [ ] [DONE] Deploy to production endpoint

## Commands to Run
```
cd ml_pipeline
pip install -r requirements_pipeline.txt
jupyter notebook medicinal_plant_training.ipynb
```
```
# After training
cp ml_pipeline/models/* backend/ml_models/
python backend/scripts/test_model_fixed.py
uvicorn backend.app.main:app --reload --port 8001
```

Current Step: 1. Dataset exploration

