# PlantoAI — Road to Production-Grade Robustness

## The 6-Stage Target Architecture (NOW LIVE)

```
User uploads WhatsApp photo
        |
[Stage 1] YOLOv8 Leaf Segmentation  ✅ DEPLOYED
  -> No leaf found -> Use full image fallback
  -> Leaf found -> crop + 10% padding
        |
[Stage 2] Gemini Vision Pre-check   ✅ DEPLOYED
  -> "Is this a plant leaf?"
  -> No (high confidence) -> Reject with message
  -> Yes / Uncertain -> Continue
        |
[Stage 3] EfficientNetV2-S ONNX     ✅ DEPLOYED
  -> 7-Pass Multi-Scale TTA Ensemble
  -> Returns top-3 with confidence scores
        |
[Stage 4] OOD Entropy Gate          ✅ DEPLOYED
  -> Entropy > 3.8 AND Conf < 12% -> "Unknown plant"
  -> Passes gate -> Continue
        |
[Stage 5] Gemini Vision Validation  ✅ DEPLOYED
  -> "Does this image match {predicted_species}?"
  -> Mismatch -> Flag warning badge in UI
  -> Confirmed -> Continue
        |
[Stage 6] Knowledge Base Lookup     ✅ DEPLOYED
  -> Ayurvedic profile from medicinal_knowledge.json
  -> Toxicity warnings
  -> Dosage guidance
  -> Gemini Vaidya enrichment
        |
Result: Grad-CAM heatmap + confidence + reasoning + vision_validation
```

---

## Sprint Execution Status (FINAL)

| Sprint | Task | Status |
|--------|------|--------|
| Sprint 1A | OOD Entropy Gate in ml_service.py | ✅ DEPLOYED |
| Sprint 1B | OOD class registered in class_names.json + KB | ✅ DEPLOYED |
| Sprint 2 | YOLOv8 leaf segmentation pipeline | ✅ DEPLOYED |
| Sprint 3 | 7-Pass Multi-Scale Ensemble TTA | ✅ DEPLOYED |
| Sprint 4 | Physical Scale Context (1-Rupee coin via Gemini) | ✅ DEPLOYED |
| Sprint 5 | Feedback Loop endpoint + Report Mismatch UI | ✅ DEPLOYED |
| Problem 5 | Class Imbalance - WeightedRandomSampler in train.py | ✅ DEPLOYED |
| Problem 6 | Single Viewpoint - RandomPerspective + Rotation(45deg) | ✅ DEPLOYED |
| Stage 2 | Gemini Vision Pre-check in predict.py | ✅ DEPLOYED |
| Stage 5 | Gemini Vision Validation in predict.py + UI badge | ✅ DEPLOYED |
| Critical Bug | OOD thresholds fixed (false rejections removed) | ✅ DEPLOYED |
| Critical Bug | Softmax sharpening removed (restored true confidence) | ✅ DEPLOYED |

---

## Commits Pushed This Session

1. `CRITICAL FIX: Remove false OOD rejection - restore accurate leaf predictions`
2. `Complete 6-Stage Pipeline: Stage2+5 Gemini Vision, Sprint5 Feedback Loop, Problem5+6 Training Fixes`
3. `Sprint 5 UI: Report Mismatch button + Stage 5 Vision Validation badge in results panel`
4. `Sprint 2: YOLOv8 Leaf Segmentation Pipeline Integration`
5. `Sprint 3 & 4: Multi-Scale Ensemble and Physical Scale Context Deployed`
6. `Night Shift: Autonomous YOLOv8 Leaf Fine-Tuning and OOD Class Registration`
7. `Sprint 1: Implement Entropy-Based Out-Of-Distribution (OOD) Gate`
8. `Fix image normalization for leaf predictions and harden config`

---

## What Needs User Action (Cannot Be Automated)

1. **Kaggle Datasets**: Download the 4 OOD weed datasets linked in the roadmap and copy images to `dataset/FINAL_MONOLITH/unknown_not_medicinal/`. Re-run `train.py` to get the full OOD-aware retrained model.
2. **Google Colab**: For EfficientNetV2-L at 384x384, run `train.py` on Colab A100 with `MODEL_NAME = "tf_efficientnetv2_l"` and `IMG_SIZE = 384`.
3. **Roboflow YOLO Dataset**: Download the leaf detection dataset from Roboflow and re-run `night_shift_yolo_train.py` with the real annotated dataset for proper leaf cropping.

---

## Morning Demo Checklist

- [ ] Open https://plantoai-backend.onrender.com/health — should show `synchronized`
- [ ] Open the Vercel frontend and upload a leaf photo
- [ ] Verify Stage 5 Vision Validation badge appears
- [ ] Verify Report Mismatch button appears below result
- [ ] Try the Symptom Search with "I have fever and cough"
- [ ] Show team the Scale Reference toggle
