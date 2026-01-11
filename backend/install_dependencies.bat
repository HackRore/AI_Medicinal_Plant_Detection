@echo off
echo 🔧 AI System - Backend Dependency Fixer
echo ----------------------------------------

echo 1. Upgrading Pip...
python -m pip install --upgrade pip

echo 2. Installing Backend Requirements...
python -m pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo ✅ All dependencies installed successfully!
    echo 🚀 You can now run: uvicorn app.main:app
) else (
    echo ❌ Installation failed. Please check the error above.
)

pause
