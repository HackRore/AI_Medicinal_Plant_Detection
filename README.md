# PlantoAI — AI Medicinal Plant Detection

PlantoAI is a high-fidelity botanical intelligence system designed to bridge traditional Ayurvedic wisdom with modern Artificial Intelligence. It features a custom-forged EfficientNetV2 engine specifically tuned for medicinal leaf morphology and clinical safety.

## 🧠 Intelligence Engine (v3.2 Production)
The system has been upgraded to **64 medicinal & botanical classes**, integrating the comprehensive **PlantDoc (IMLD)** dataset. 

### 📐 Species Intelligence Tiers:
- **Ayurvedic Core**: Tulsi, Neem, Arjun, Bael, Aloe Vera, and 30+ traditional herbs.
- **Agricultural Core**: Tomato, Potato, Corn, Wheat, Soybean, and fruit varieties.
- **Disease Intelligence**: Detection for diseases like Late Blight, Scab, and Rust variants across major species.

## 🚀 Key Features
- 🔍 **Neural Forge**: Real-time identification with **97.21% Precision** (Top-1).
- 🧠 **Morphological Explainability**: Integrated Grad-CAM heatmaps showing precise neural attention.
- 📚 **Medicinal Wisdom Layer**: Dynamic lookup for Scientific nomenclature, Ayurvedic preparations, and Toxicity levels.
- ⚙️ **Lean Architecture**: Repository purged of legacy assets (v3.2 Purge) for optimized maintenance and lightning-fast cloud deployment.
- **Architecture**: EfficientNetV2-S (ImageNet-21k fine-tuned)
- **Engine**: ONNX Runtime (Opset 18)
- **Backend**: FastAPI (Python 3.10+)
- **Explainability**: Occlusion-based Grad-CAM
- **Frontend**: Next.js 14 (Tailwind + Framer Motion)

## 🛠️ Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
API docs: `http://127.0.0.1:8000/docs`

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
App: `http://localhost:3000`

## 🏁 Deployment
The project is optimized for deployment on Vercel (Frontend) and Render/Railway (Backend).

---
Developed by **Group G9 (Botanical Engine Team)** 🏅🎯🏁🚩🏆🏁🏆
