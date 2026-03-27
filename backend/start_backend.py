import subprocess
import os
import sys
import time

# Mock environment
os.environ["DATABASE_URL"] = "postgresql://postgres:PlantoAi%405665@db.bcyiaopmtmpqrjijtygu.supabase.co:5432/postgres"
os.environ["GEMINI_API_KEY"] = "AIzaSyC9oP0Mn7p6L6UYdeFA5g5Z_pui2aPQdUE"

# Path to venv
venv_python = os.path.join("venv", "Scripts", "python.exe")

print("Starting backend with Uvicorn...")
process = subprocess.Popen(
    [venv_python, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=open("logs/app_stdout.log", "w"),
    stderr=open("logs/app_stderr.log", "w"),
    cwd=os.getcwd()
)

print(f"Backend started with PID {process.pid}")
time.sleep(5)
print("Startup complete. Check logs/app_stderr.log for errors.")
