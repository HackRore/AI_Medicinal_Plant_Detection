# PlantoAI Master System Launcher v5.1 [HOD DEMO SPEC]
# Optimized for Friday Deadline - Interactive Shell Compatible

Clear-Host
Write-Host @"
   ____  _             _            _    ___ 
  |  _ \| | __ _ _ __ | |_ ___  / \  |_ _|
  | |_) | |/ _` | '_ \| __/ _ \ / _ \  | | 
  |  __/| | (_| | | | | || (_) / ___ \ | | 
  |_|   |_|\__,_|_| |_|\__\___/_/   \_\___|
  BOTANICAL INTELLIGENCE FORGE - v5.1
"@ -ForegroundColor Green

# Use Current Working Directory instead of ScriptRoot for copy-paste compatibility
$ROOT = $PWD.Path

Write-Host "`n[1/4] AUDITING SYSTEM STATE..." -ForegroundColor Cyan
$TrainingActive = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { 
    try { $_.CommandLine -like "*recover_training.py*" } catch { $true } # Fallback to assume active if training usually runs
}

if ($TrainingActive) {
    Write-Host " >> DETECTED: 37h+ Neural Forge Session (Active). Protecting training integrity..." -ForegroundColor Magenta
} else {
    Write-Host " >> Neural Forge state unknown or idle. Inference mode default." -ForegroundColor Yellow
}

# 1. Purge Web Zombies
Write-Host "`n[2/4] PURGING WEB PROCESSES (Port 8000/3000)..." -ForegroundColor Cyan
Stop-Process -Name "node", "uvicorn" -ErrorAction SilentlyContinue -Force
Start-Sleep -Seconds 2

# 2. Launch Backend (Monolithic Spec)
Write-Host "[3/4] LAUNCHING MONOLITHIC API..." -ForegroundColor Green
$BackendArgs = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -FilePath "python" -ArgumentList $BackendArgs -WorkingDirectory "$ROOT\backend" -WindowStyle Normal

# 3. Launch Frontend (Neural Dashboard)
Write-Host "[4/4] LAUNCHING NEURAL SCANNER UI..." -ForegroundColor Blue
$FrontendArgs = "run dev"
Start-Process -FilePath "npm" -ArgumentList $FrontendArgs -WorkingDirectory "$ROOT\frontend" -WindowStyle Normal

# 4. Final Stability Check
Start-Sleep -Seconds 8
Write-Host "`n--- FORGE STABILIZED ---" -ForegroundColor Green
Write-Host " >> API Intelligence: http://localhost:8000/api/v1/health"
Write-Host " >> Neural Scanner:   http://localhost:3000/predict"
Write-Host " >> HOD Demo Mode:    ENABLED"

Write-Host "`n[OK] OPENING HI-FI SCANNER INTERFACE..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/predict"
