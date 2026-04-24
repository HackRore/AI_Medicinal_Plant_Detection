import os
from dotenv import load_dotenv
from supabase import create_client

print("Loading .env...")
load_dotenv('backend/.env')
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

print(f"URL: {URL}")
print(f"KEY: {KEY[:10]}...")

print("Creating client...")
try:
    supabase = create_client(URL, KEY)
    print("Client created successfully!")
    print("Testing connection...")
    # Just try to get something
    res = supabase.table("medicinal_plants").select("count", count="exact").limit(0).execute()
    print(f"Connection test result: {res}")
except Exception as e:
    print(f"Error: {e}")
