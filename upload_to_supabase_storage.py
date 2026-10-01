"""
Script per caricare le immagini su Supabase Storage e aggiornare le URL nel DB.
"""

import os
import sys
from pathlib import Path
import httpx
from backend.config import SUPABASE_URL, SUPABASE_REST_URL, SUPABASE_KEY

# Encoding UTF-8 per console Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BUCKET_NAME = "scarpe-images"
IMAGES_DIR = Path("./backend/static/images")

HEADERS_STORAGE = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "x-upsert": "true"
}

HEADERS_DB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_mime_type(ext: str) -> str:
    ext = ext.lower()
    if ext in ('.jpg', '.jpeg'):
        return 'image/jpeg'
    elif ext == '.png':
        return 'image/png'
    elif ext == '.webp':
        return 'image/webp'
    elif ext == '.gif':
        return 'image/gif'
    return 'application/octet-stream'

def main():
    if not IMAGES_DIR.exists():
        print(f"Cartella {IMAGES_DIR} non trovata!")
        return

    files = list(IMAGES_DIR.glob("*.*"))
    print(f"Trovate {len(files)} immagini da caricare nel bucket '{BUCKET_NAME}'...")

    uploaded_count = 0
    error_count = 0

    with httpx.Client(timeout=30.0, verify=False) as client:
        # Prendi tutte le scarpe dal DB
        print("Recupero record scarpe dal database Supabase...")
        r_shoes = client.get(f"{SUPABASE_REST_URL}/shoes?select=id,image_url", headers=HEADERS_DB)
        if r_shoes.status_code != 200:
            print(f"Errore lettura DB: {r_shoes.status_code} - {r_shoes.text}")
            return
        
        shoes_db = r_shoes.json()
        print(f"Trovate {len(shoes_db)} scarpe nel DB Supabase.")

        # Mappa filename -> list of shoe IDs
        filename_to_shoes = {}
        for s in shoes_db:
            url = s.get("image_url", "")
            if url and "/static/images/" in url:
                fn = url.split("/static/images/")[-1]
                filename_to_shoes.setdefault(fn, []).append(s["id"])

        for idx, file_path in enumerate(files, 1):
            filename = file_path.name
            mime_type = get_mime_type(file_path.suffix)
            
            # Leggi i byte del file
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{filename}"
            h = {**HEADERS_STORAGE, "Content-Type": mime_type}

            resp = client.post(upload_url, content=file_bytes, headers=h)

            if resp.status_code in (200, 201):
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{filename}"
                uploaded_count += 1

                # Se questa immagine è collegata ad una o più scarpe nel DB, aggiorna la colonna image_url
                if filename in filename_to_shoes:
                    for shoe_id in filename_to_shoes[filename]:
                        patch_payload = {"image_url": public_url}
                        client.patch(
                            f"{SUPABASE_REST_URL}/shoes?id=eq.{shoe_id}",
                            json=patch_payload,
                            headers=HEADERS_DB
                        )
                if idx % 20 == 0 or idx == len(files):
                    print(f"Caricate {idx}/{len(files)} immagini...")
            else:
                error_count += 1
                if "violates row-level security policy" in resp.text:
                    print(f"\n❌ ERRORE POLICY RLS: Supabase richiede la policy di Upload sul bucket '{BUCKET_NAME}'.")
                    print(resp.text)
                    return
                print(f"Errore upload {filename}: {resp.status_code} - {resp.text}")

    print(f"\n✅ Operazione completata! Caricate: {uploaded_count}, Errori: {error_count}")

if __name__ == "__main__":
    main()
