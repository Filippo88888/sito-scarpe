import os
from pathlib import Path
from dotenv import load_dotenv

# Cerca il file .env nella root del progetto o nella cartella backend
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(dotenv_path=env_path)

raw_url = os.getenv("SUPABASE_URL", "").strip()
# Rimuove /rest/v1 o trailing slash se presente
if raw_url.endswith("/rest/v1/"):
    raw_url = raw_url[:-9]
elif raw_url.endswith("/rest/v1"):
    raw_url = raw_url[:-8]
SUPABASE_URL = raw_url.rstrip("/")

SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1" if SUPABASE_URL else ""
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
PORT = int(os.getenv("BACKEND_PORT", 8000))
