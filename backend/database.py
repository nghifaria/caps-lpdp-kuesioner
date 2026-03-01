import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Memuat environment variables
load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Kredensial Supabase (URL atau KEY) tidak ditemukan di environment variables.")

# Inisialisasi secara konsisten dan aman
try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Error inisialisasi client Supabase: {e}")
    raise e
