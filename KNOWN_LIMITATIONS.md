# PlantoAI — Known Limitations & Realities

For full transparency with stakeholders, the following limitations exist in the current V3.1 deployment:

### 1. The 46/88 Species Gap
While the botanical registry contains knowledge profiles for 88 medicinal plants, the core EfficientNetV2-S visual classifier is currently trained on **46 distinct species**. The remaining 42 profiles are accessible via the Symptom Search (RAG Engine) but cannot be visually identified by the camera until the dataset is expanded and retrained.

### 2. Render Cold-Start Delay (Free Tier)
The backend is hosted on Render's free tier. If the service receives no traffic for 15 minutes, it spins down to save resources. **The first inference/API call after a period of inactivity may take up to 30-50 seconds** as the Docker container wakes up, reloads the OS, and loads the ML models into RAM. Subsequent requests will process rapidly. (This is immediately resolved by upgrading to a paid tier).

### 3. Real-World vs. Lab Accuracy
The model achieved high accuracy on validation sets, but field conditions introduce chaos. Variations in lighting, shadows, camera blur, and overlapping flora can reduce confidence scores. The **Stage 4 OOD Gate** is designed to catch uncertain predictions, but users should ensure leaves are well-lit and isolated for best results.

### 4. Not Medical Advice
The **Symptom Search** and Ayurvedic monographs provided by the Gemini Reasoning Engine (`gemini-1.5-pro`) are for educational and traditional knowledge preservation purposes only. **PlantoAI is not a substitute for professional medical advice, diagnosis, or treatment.** Users should always consult a certified Vaidya or healthcare professional before preparing or consuming plant-based remedies.
