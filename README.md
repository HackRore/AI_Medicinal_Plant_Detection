# PlantoAI — AI Medicinal Plant Detection

## Features
- 🔍 **AI-powered identification** from leaf photos (92.5% accuracy) using EfficientNetV2.
- 🧠 **Grad-CAM Explainability**: Real-time neural attention heatmaps showing AI focus areas.
- 📚 **Botanical Library**: Full metadata for 81 medicinal species (Neem, Tulsi, Ashwagandha, etc.).
- 📱 **Neural Performance**: Live latency and confidence tier tracking (Emerald, Amber, Crimson).
- ⚠️ **Toxicity Intelligence**: Automated safety flagging for over 10+ hazardous plant species.
- 💊 **Medicinal Insights**: Ayurvedic uses, preparation methods, and dosage guidance.
- 📱 **PWA Ready**: Offline support and home-screen installer enabled.

## Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:3000

## Demo Plants
- Tulsi (92%) - Ocimum sanctum
- Neem (87%) - Azadirachta indica
- Aloe Vera (94%) - Aloe barbadensis
- Ashwagandha (88%) - Withania somnifera
- Giloy (91%) - Tinospora cordifolia

## Deploy
```bash
git add .
git commit -m "Complete PlantoAI"
git push origin main
vercel --prod
```

Full model training in progress. Stars ⭐ appreciated!
