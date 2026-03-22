# 🚀 AI Refactor Phase (Day 2) - Implementation Guide

**Branch**: `ai-refactor`  
**Status**: ✅ Scaffolding Complete, Ready for Training Data Integration  
**Timeline**: Day 2 (Implemented), Day 3 (Fine-tune & deploy)

---

## 📋 What's Implemented

### ✅ Backend Infrastructure

#### 1. **Quality Gatekeeper Module** (`ml_pipeline/models/quality_gatekeeper.py`)
   - **Blur Detection**: Laplacian variance (target: >100)
   - **Brightness Analysis**: Range 30-225
   - **Composition Scoring**: Object size 15-90% of frame
   - **Output**: JSON with pass/fail + recommendations
   - **Usage**:
     ```python
     from ml_pipeline.models.quality_gatekeeper import quality_check
     result = quality_check(image_bytes, strict=False)
     # result: { is_valid, scores, reasons, recommendations }
     ```

#### 2. **Quality Check API Route** (`backend/app/api/v1/quality_check.py`)
   - `POST /api/v1/quality-check/` - Standard quality check
   - `POST /api/v1/quality-check/strict` - Stricter thresholds
   - **Response**: Detailed quality metrics + feedback
   - **Frontend Integration**: Pre-prediction validation

#### 3. **Hybrid Model Skeleton** (`ml_pipeline/models/efficientnet_swin.py`)
   - **Architecture**:
     - EfficientNetV2-S: Fast feature extraction (1280 channels)
     - Multi-Scale Attention: Transformer blocks for refinement
     - Confidence Head: Separate confidence estimation
     - Classification Head: Plant species prediction
   - **Features**:
     - Attention maps for explainability
     - Per-class confidence scoring
     - Modular design for easy updates
   - **Usage**:
     ```python
     from ml_pipeline.models.efficientnet_swin import EfficientNetSwinHybrid
     model = EfficientNetSwinHybrid(num_classes=40)
     output = model(image_tensor)
     # output: { logits, probabilities, confidence, attention_maps, features }
     ```

#### 4. **Training Script** (`ml_pipeline/train_hybrid_model.py`)
   - PyTorch Lightning integration
   - Automatic data loading from `/data/training`
   - Quality filtering support
   - 70/15/15 train/val/test split
   - Early stopping + best checkpoint saving
   - **Usage**:
     ```bash
     python ml_pipeline/train_hybrid_model.py \
       --data-dir data/training \
       --epochs 100 \
       --batch-size 32 \
       --quality-check
     ```

### ✅ Frontend Components

#### 1. **Quality Check Utility** (`frontend/utils/qualityCheck.ts`)
   - `checkImageQuality(file, strict)` - Call backend quality API
   - `formatQualityFeedback()` - Format results for UI
   - `getConfidenceLevel()` - Map confidence to descriptive text
   - **TypeScript interfaces** for type safety

#### 2. **Quality Feedback Component** (`frontend/components/QualityFeedback.tsx`)
   - Visual quality assessment display
   - Pass/fail indicators
   - Metric breakdown
   - User recommendations
   - Animated feedback

#### 3. **Confidence Display Component** (`frontend/components/QualityFeedback.tsx`)
   - Animated confidence bar
   - Percentage display
   - Confidence level indicator
   - Top 3 alternative predictions
   - Educational disclaimer

---

## 📁 Data Structure for Training

Created: `/data/training/` directory with template structure

```
data/training/
├── Neem/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ... (20+ images per species)
├── Tulsi/
├── Turmeric/
├── Mint/
├── Aloe/
└── ... (other species)
```

### Data Requirements:
- **Format**: JPG/PNG
- **Resolution**: 224x224+ (512x512 recommended)
- **Images per class**: 20+ (100+ for production)
- **Total dataset**: 40+ plant species = 800-4000 images
- **Quality**: Must pass quality gatekeeper checks

---

## 🎯 Integration Points

### Backend API Flow
```
User Upload Image
    ↓
/api/v1/quality-check/
    ↓ (quality_gatekeeper.py processes)
    ↓
Return quality metrics + feedback
    ↓ (if passed)
    ↓
/api/v1/predict/
    ↓ (efficientnet_swin.py inference)
    ↓
Return predictions + confidence + attention maps
```

### Frontend Flow
```
User Selects Image
    ↓
Show uploading spinner
    ↓
Call checkImageQuality()
    ↓
Display <QualityFeedback />
    ↓ (if failed, show recommendations)
    ↓ (if passed)
    ↓
Call API predict endpoint
    ↓
Display <ConfidenceDisplay /> with results
    ↓
Show heatmap overlay (attention maps)
```

---

## 🔧 Integration TODOs for Day 2

### Phase 1: Update Frontend Prediction Page
```typescript
// In frontend/app/predict/page.tsx

import { checkImageQuality } from '@/utils/qualityCheck'
import { QualityFeedback, ConfidenceDisplay } from '@/components/QualityFeedback'

// Add quality check before prediction
const checkQualityMutation = useMutation({
  mutationFn: async (file: File) => {
    return checkImageQuality(file, false) // or true for strict
  },
  onSuccess: async (qualityResult) => {
    if (!qualityResult.is_valid) {
      setQualityIssues(qualityResult) // Display feedback
      return
    }
    // Proceed with prediction
    predictMutation.mutate(file)
  }
})

// Render quality feedback
{qualityIssues && <QualityFeedback result={qualityIssues} />}

// Render confidence display
{prediction && <ConfidenceDisplay confidence={prediction.confidence} topPredictions={prediction.top_predictions} />}
```

### Phase 2: Test with Sample Data
```bash
# Copy sample images to training directories
cp sample_images/neem/* data/training/Neem/
cp sample_images/tulsi/* data/training/Tulsi/

# Run training (will use placeholder backbone initially)
python ml_pipeline/train_hybrid_model.py \
  --data-dir data/training \
  --epochs 10 \
  --batch-size 16 \
  --quality-check
```

### Phase 3: Replace Placeholder Backbone
Once PyTorch models are fully installed, update `efficientnet_swin.py`:

```python
# Instead of placeholder, use timm:
from timm import create_model

self.backbone = create_model(
    'efficientnetv2_s',
    pretrained=True,
    num_classes=0
)
```

---

## 📊 Model Architecture Summary

```
Input Image (B, 3, 224, 224)
    ↓
[EfficientNetV2-S Backbone]
    ↓ (Feature extraction)
    ↓ (B, 1280, 7, 7) features
    ↓
[Multi-Scale Attention Refiner]
    ↓ (2x Transformer blocks)
    ↓ (Attention-based refinement)
    ↓ (B, 1280, 7, 7) refined features
    ↓
[Global Average Pooling]
    ↓ (B, 1280) pooled features
    ↓
┌─────────────────────────────┐
│                             │
├─→ [Confidence Head]     ├─→ Sigmoid(confidence per class)
│   (512 → 256 → 40)      │
│                             │
├─→ [Classifier Head]     ├─→ Softmax(logits)
│   (512 → 256 → 40)      │
│                             │
└─────────────────────────────┘
    ↓
Output: {
  logits: (B, 40),
  probabilities: (B, 40),
  confidence: (B, 40),
  attention_maps: List[(B, HW, HW)],
  features: (B, 1280)
}
```

---

## 🚀 Next Steps

### Immediate (Complete Today):
1. ✅ Review all code files
2. ✅ Verify API routes registered
3. ✅ Test quality check endpoint
4. Prepare dataset (download/organize images)

### Tomorrow (Day 2 Training):
1. Add images to `/data/training/Plant_Name/`
2. Run training script
3. Monitor validation metrics
4. Save best model checkpoint
5. Export to ONNX format
6. Update predict service to use new model
7. Commit changes to `ai-refactor` branch

### Day 3 (Final Polish):
1. Merge `ai-refactor` → `main`
2. Deploy to Vercel
3. Final testing
4. Add disclaimers & documentation

---

## 📝 File Checklist

### Backend
- ✅ `ml_pipeline/models/quality_gatekeeper.py`
- ✅ `ml_pipeline/models/efficientnet_swin.py`
- ✅ `backend/app/api/v1/quality_check.py`
- ✅ `backend/app/main.py` (updated with quality_check router)
- ✅ `ml_pipeline/train_hybrid_model.py`

### Frontend
- ✅ `frontend/utils/qualityCheck.ts`
- ✅ `frontend/components/QualityFeedback.tsx`
- 🔲 `frontend/app/predict/page.tsx` (integration pending - use as template)

### Data
- ✅ `data/training/` directory structure
- ✅ `data/training/README.md` (dataset guide)

### Documentation
- ✅ This file: `AI_REFACTOR_GUIDE.md`

---

## 🔗 API Endpoint Summary

### Quality Check
```
POST /api/v1/quality-check/
Content-Type: multipart/form-data
Body: { file: Image }
Response: {
  is_valid: bool,
  scores: { blur: float, brightness: bool, composition: bool },
  reasons: [str],
  recommendations: [str],
  image_shape: [int, int, int],
  image_size_mb: float
}
```

### Prediction (Enhanced)
```
POST /api/v1/predict/
Content-Type: multipart/form-data
Body: { file: Image }
Response: {
  predicted_class: str,
  confidence: float,
  confidence_scores: {class: float},  // NEW
  top_predictions: [{class, conf}, ...],
  attention_maps: ...,  // NEW - Grad-CAM
  processing_time_ms: float,
  ...other_fields
}
```

---

## 🎓 Educational Notes

- Quality gatekeeper acts as "pre-filter" before ML model
- Confidence scoring allows model to express uncertainty
- Attention maps make predictions explainable (Grad-CAM style)
- Modular design = easy to swap architectures later

---

## ✨ Ready for Production?

**Current Status**: 🟡 Scaffolding + Ready for Training Phase

**Path to Production**:
1. ✅ API infrastructure (done)
2. ✅ Frontend hooks (done)
3. ⏳ Train model on dataset (tomorrow)
4. ⏳ Export & deploy (tomorrow afternoon)
5. ⏳ Final testing (day 3)

---

**Questions?** Check `/data/training/README.md` for data setup questions, or review component code for integration questions.

**Ready to train?**
```bash
# Organize your data, then run:
python ml_pipeline/train_hybrid_model.py --data-dir data/training --quality-check
```
