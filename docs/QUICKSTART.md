# Quick Start Guide - AI Medicinal Plant Detection

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

## Option 1: Docker (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/HackRore/AI_Medicinal_Plant_Detection.git
cd AI_Medicinal_Plant_Detection
```

### 2. Start Services
```bash
cd infrastructure/docker
docker-compose up -d
```

### 3. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Option 2: Manual Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

---

## Using the Application

### 1. Identify a Plant

1. Go to http://localhost:3000/predict
2. Upload or drag-and-drop a leaf image
3. Click "Identify Plant"
4. View prediction results with confidence score

### 2. Explore Plant Information

1. Go to http://localhost:3000/plants
2. Browse available medicinal plants
3. Click on a plant to see detailed information
4. Learn about medicinal properties and uses

### 3. API Usage

```python
import requests

# Upload image for prediction
with open('leaf.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/predict/',
        files={'file': f}
    )
    
prediction = response.json()
print(f"Plant: {prediction['predicted_plant']}")
print(f"Confidence: {prediction['confidence']}")
```

---

## Training ML Models

### Download Dataset

1. Download [Indian Medicinal Leaves Dataset](https://www.kaggle.com/datasets/aryashah2k/indian-medicinal-leaves-dataset)
2. Extract to `dataset/Indian Medicinal Leaves Image Datasets/`

### Train MobileNetV2

```bash
cd ml_pipeline
python train_mobilenet.py
```

This will:
- Train the model with data augmentation
- Generate evaluation metrics
- Export to ONNX format
- Save to `ml_pipeline/models/`

---

## Configuration

### Backend (.env)

Create `backend/.env`:

```env
# Application
DEBUG=True
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=sqlite:///./medicinal_plants.db

# ML Models
MODEL_DIR=./ml_models

# Google Gemini (optional)
GEMINI_API_KEY=your-api-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

Create `frontend/.env.local`:

```env
API_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed
- Check if port 8000 is available
- Verify all dependencies are installed

### Frontend won't start
- Ensure Node.js 18+ is installed
- Delete `node_modules` and `.next`, then run `npm install`
- Check if port 3000 is available

### Prediction fails
- Ensure backend is running
- Check image file size (max 10MB)
- Verify image format (JPG/PNG)

### Database errors
- Run `python scripts/seed_data.py` to initialize database
- Delete `medicinal_plants.db` and reseed if corrupted

---

## Next Steps

- Read the [API Reference](api-reference.md)
- Train custom models with your dataset
- Configure Gemini API for AI descriptions
- Deploy to production (see deployment guide)

---

## Support

- **GitHub Issues**: https://github.com/HackRore/AI_Medicinal_Plant_Detection/issues
- **Email**: hackrore@gmail.com
- **Documentation**: See `docs/` directory
