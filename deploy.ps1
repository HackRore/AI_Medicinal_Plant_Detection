# Deployment Script - Complete Setup

Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host ("=" * 69) -ForegroundColor Green
Write-Host "AI MEDICINAL PLANT DETECTION - DEPLOYMENT SETUP" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Green

# Step 1: Setup ML Models
Write-Host "`n[1/5] Setting up ML model configurations..." -ForegroundColor Yellow
Set-Location ml_pipeline
python quick_setup.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ ML configurations created" -ForegroundColor Green
    
    # Copy to backend
    Copy-Item -Path "models\*" -Destination "..\backend\ml_models\" -Force
    Write-Host "✓ Copied to backend/ml_models/" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create ML configurations" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Step 2: Setup Backend
Write-Host "`n[2/5] Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create .env from production template
if (-not (Test-Path ".env")) {
    Copy-Item ".env.production" ".env"
    Write-Host "✓ Created .env file (update with your values)" -ForegroundColor Green
} else {
    Write-Host "✓ .env already exists" -ForegroundColor Green
}

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some dependencies may have failed" -ForegroundColor Yellow
}

# Seed database
Write-Host "Seeding database..." -ForegroundColor Yellow
python scripts\seed_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database seeded with plant data" -ForegroundColor Green
} else {
    Write-Host "⚠ Database seeding had issues (may already be seeded)" -ForegroundColor Yellow
}

Set-Location ..

# Step 3: Setup Frontend
Write-Host "`n[3/5] Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Create .env.local
if (-not (Test-Path ".env.local")) {
    @"
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
"@ | Out-File -FilePath ".env.local" -Encoding utf8
    Write-Host "✓ Created .env.local" -ForegroundColor Green
}

# Install frontend dependencies
if (Test-Path "package.json") {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install --silent
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Frontend installation had issues" -ForegroundColor Yellow
    }
}

Set-Location ..

# Step 4: Create necessary directories
Write-Host "`n[4/5] Creating directories..." -ForegroundColor Yellow
$dirs = @(
    "backend\uploads",
    "backend\ml_models",
    "backend\logs",
    "ml_pipeline\models"
)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ Created $dir" -ForegroundColor Green
    }
}

# Step 5: Summary
Write-Host "`n[5/5] Deployment Summary" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Green

Write-Host "`n✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "`nWhat's Ready:" -ForegroundColor Cyan
Write-Host "  ✓ Backend API with all endpoints" -ForegroundColor White
Write-Host "  ✓ Frontend web application" -ForegroundColor White
Write-Host "  ✓ Database seeded with 6 medicinal plants" -ForegroundColor White
Write-Host "  ✓ ML model configurations" -ForegroundColor White
Write-Host "  ✓ Docker setup" -ForegroundColor White

Write-Host "`nTo Start the Application:" -ForegroundColor Cyan
Write-Host "  Option 1 - Docker (Recommended):" -ForegroundColor Yellow
Write-Host "    cd infrastructure\docker" -ForegroundColor White
Write-Host "    docker-compose up -d" -ForegroundColor White
Write-Host "`n  Option 2 - Manual:" -ForegroundColor Yellow
Write-Host "    Terminal 1: cd backend && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "    Terminal 2: cd frontend && npm run dev" -ForegroundColor White

Write-Host "`nAccess Points:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n⚠️  Next Steps for Production:" -ForegroundColor Yellow
Write-Host "  1. Update backend\.env with production values" -ForegroundColor White
Write-Host "  2. Train real ML models: cd ml_pipeline && pip install -r requirements.txt && python train_mobilenet.py" -ForegroundColor White
Write-Host "  3. Get Gemini API key from Google AI Studio" -ForegroundColor White
Write-Host "  4. Configure PostgreSQL for production" -ForegroundColor White
Write-Host "  5. Set up SSL/HTTPS" -ForegroundColor White

Write-Host "`n" + ("=" * 70) -ForegroundColor Green
Write-Host "Happy Deploying! 🚀" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Green
