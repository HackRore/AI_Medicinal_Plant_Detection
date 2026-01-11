# Simple Deployment Setup Script
# Run this to set up the project for deployment

Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host "AI MEDICINAL PLANT DETECTION - SETUP"
Write-Host ("=" * 70)

# Setup ML configurations
Write-Host "`nSetting up ML configurations..." -ForegroundColor Yellow
Set-Location ml_pipeline
python quick_setup.py
Set-Location ..

# Copy models to backend
Write-Host "Copying model configs to backend..." -ForegroundColor Yellow
Copy-Item -Path "ml_pipeline\models\*" -Destination "backend\ml_models\" -Force -ErrorAction SilentlyContinue

# Create .env for backend
Write-Host "Creating backend .env file..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
}

# Create .env.local for frontend
Write-Host "Creating frontend .env.local file..." -ForegroundColor Yellow
Set-Content -Path "frontend\.env.local" -Value "API_URL=http://localhost:8000"

Write-Host "`n" -NoNewline
Write-Host ("=" * 70)
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 70)

Write-Host "`nTo start the application:" -ForegroundColor Cyan
Write-Host "  1. Backend:  cd backend && pip install -r requirements.txt && python scripts\seed_data.py && uvicorn app.main:app --reload"
Write-Host "  2. Frontend: cd frontend && npm install && npm run dev"
Write-Host "`nOr use Docker: cd infrastructure\docker && docker-compose up"

Write-Host "`nAccess at:"
Write-Host "  Frontend: http://localhost:3000"
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  API Docs: http://localhost:8000/docs"
Write-Host ""
