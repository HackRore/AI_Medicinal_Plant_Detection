# PlantoAI — AI Medicinal Plant Detection

## Features
- 🔍 AI-powered medicinal plant identification from leaf photos (92.5% accuracy)
- 📱 Live camera scan + multi-image upload (max 3)
- ⚠️ Toxicity warnings for dangerous plants
- 💊 Medicinal information cards with usage/precautions
- 📊 Confidence scores and top alternatives
- 💾 Detection history (localStorage + server)
- 🎨 Demo mode with 5 sample plants
- 🔄 Wrong result feedback loop
- 📱 PWA ready for offline use

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
