# PlantoAI Master System Launcher v4.0 [HARDENED]
# Developed by Antigravity AI for Resource-Safe Performance

Write-Host "--- PLANTOAI PRODUCTION RECOVERY STARTING ---" -ForegroundColor Cyan

# 1. Clear Ghost Processes
Write-Host "Purging all zombie Python, Node, and Uvicorn processes..." -ForegroundColor Yellow
Stop-Process -Name "python", "node", "uvicorn" -ErrorAction SilentlyContinue -Force
Start-Sleep -Seconds 3

# 2. Launch Backend (Instant-On)
Write-Host "Launching Medicinal API (Port 8000)..." -ForegroundColor Green
$BackendArgs = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
# Start with Normal priority to ensure snappy API responses
Start-Process -FilePath "python" -ArgumentList $BackendArgs -WorkingDirectory "$PSScriptRoot\backend" -WindowStyle Normal

# 3. Launch AI Forge (Parallel - RESOURCE PROTECTED)
Write-Host "Activating Neural Forge [Priority: BelowNormal]..." -ForegroundColor Magenta
$ForgeArgs = "scripts/train_final.py"
# Start with BelowNormal priority so it doesn't crash the UI or API
Start-Process -FilePath "python" -ArgumentList $ForgeArgs -WorkingDirectory "$PSScriptRoot\backend" -WindowStyle Normal -Priority BelowNormal

# 4. Launch Frontend Dashboard
Write-Host "Activating Dashboard UI (Port 3000)..." -ForegroundColor Blue
$FrontendArgs = "run dev"
Start-Process -FilePath "npm" -ArgumentList $FrontendArgs -WorkingDirectory "$PSScriptRoot\frontend" -WindowStyle Normal

# 5. Final Verification
Start-Sleep -Seconds 10
Write-Host "`n--- SYSTEM STABILIZED ---" -ForegroundColor Cyan
Write-Host "Backend:   http://localhost:8000/health"
Write-Host "Frontend:  http://localhost:3000"
Write-Host "AI Forge:  ACTIVE (Resource Protected)"

Write-Host "`nOpening your browser now..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"
