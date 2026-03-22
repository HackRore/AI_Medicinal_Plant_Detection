# Backend deployment notes

This backend is a FastAPI application that serves the Medicinal Plant Detection API.

Local run (development):

1. Create a virtual environment and activate it.

```powershell
python -m venv .venv
& .\.venv\\Scripts\\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add environment variables. Create a `.env` file in `backend/` with at minimum:

```
SECRET_KEY=your_secret_here
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
GEMINI_API_KEY=
```

4. Start the app:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Notes for production deployment:

- Do NOT commit `.env` or secret keys. Use a secret manager.
- The ML models are expected under `backend/ml_models/` (ONNX or .h5). If missing, the service will run in demo mode.
- For GPU acceleration, configure ONNX Runtime with the CUDA provider.
