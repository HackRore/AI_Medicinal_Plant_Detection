import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://bcyiaopmtmpqrjijtygu.supabase.co")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
