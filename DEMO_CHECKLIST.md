# PlantoAI Production Demo Checklist

**Pre-Flight Check:**
- [ ] Backend is awake: Navigate to `https://plantoai-backend.onrender.com/health` and confirm `{"status":"synchronized"}`.
- [ ] Frontend is live on Vercel.

**1. The 6-Stage Pipeline Test**
Upload a clear leaf image and talk the audience through the real-time processing:
- [ ] **Stage 1 (YOLOv8 Segmentation):** Explain how the system isolates the leaf and ignores the background.
- [ ] **Stage 2 (Gemini Gatekeeper):** Mention the vision pre-check verifying it's actually a plant.
- [ ] **Stage 3 (EfficientNetV2-S ONNX):** Highlight the 7-pass multi-scale ensemble doing the heavy lifting.
- [ ] **Stage 4 (OOD Entropy Gate):** Note the mathematical certainty check against weeds/unknowns.
- [ ] **Stage 5 (Gemini Validation):** Show the **Vision Validation Badge** on the UI confirming ML aligns with visual logic.
- [ ] **Stage 6 (Knowledge Base):** Scroll down to the rich Ayurvedic profile, toxicity, and dosage guidance.

**2. UI & Feedback Loop Features**
- [ ] **Mismatch Reporting:** Click the "Report Mismatch" button to demonstrate the continuous learning feedback loop.
- [ ] **Symptom Search (RAG Engine):** Enter "I have a fever and cough" into the Symptom Search and show the AI Vaidya's grounded recommendation.
- [ ] **Scale Reference:** Toggle the 1-Rupee Scale Reference to demonstrate physical scaling context for field users.
