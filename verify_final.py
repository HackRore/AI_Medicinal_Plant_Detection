import os
import sys
import json
import sqlite3
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend/.env
load_dotenv('backend/.env')

def test_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("❌ Supabase credentials missing in .env")
        return
    
    try:
        supabase: Client = create_client(url, key)
        response = supabase.table("medicinal_plants").select("*").limit(1).execute()
        if len(response.data) > 0:
            print(f"[SUCCESS] Supabase Connectivity: Found: {response.data[0]['scientific_name']}")
        else:
            print("[SUCCESS] Supabase Connectivity: But table is empty")
    except Exception as e:
        print(f"[FAILED] Supabase Connectivity: ({e})")

def test_local_sqlite():
    db_path = 'backend/plantoai.db'
    if not os.path.exists(db_path):
        print(f"[WARNING] Local SQLite: NOT FOUND at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"[SUCCESS] Local SQLite: Tables: {[t[0] for t in tables]}")
        conn.close()
    except Exception as e:
        print(f"[FAILED] Local SQLite: ({e})")

def test_model_presence():
    model_path = 'backend/ml_models/best.pt'
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"[SUCCESS] Neural Weights: PRESENT ({size_mb:.2f} MB)")
    else:
        print("[PENDING] Neural Weights: PENDING (Training in progress)")

if __name__ == "__main__":
    print("\n=== FINAL PRODUCTION AUDIT ===")
    test_supabase()
    test_local_sqlite()
    test_model_presence()
    print("==============================\n")
