"""
Script per l'importazione automatica di foto da un archivio locale.

Formato nome generato: Marca Modello-Numero (es. "NB 9060-001")
Salva la sottocartella (Modello) nel campo description per consentire il filtraggio per modello nel frontend.
"""

import os
import sys
import re
import shutil
from pathlib import Path
import httpx
from backend.config import SUPABASE_REST_URL, SUPABASE_KEY

# Imposta encoding UTF-8 per il terminale Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Disabilita avvisi SSL per sviluppo locale
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurazione cartelle
ARCHIVIO_DIR = Path("./archivio_foto")
STATIC_DEST_DIR = Path("./backend/static/images")
BASE_URL = "http://localhost:8000/static/images"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def slugify(text: str) -> str:
    """Converte una stringa in uno slug pulito per URL."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)

def extract_number(filename: str, fallback_idx: int) -> str:
    """Estrae il numero dal nome file (es. foto_013 -> 013)."""
    digits = re.findall(r'\d+', filename)
    if digits:
        # Prendi l'ultimo gruppo di cifre
        num = digits[-1]
        # Garantisci almeno 3 cifre (es. 1 -> 001)
        if len(num) < 3 and num.isdigit():
            return f"{int(num):03d}"
        return num
    return f"{fallback_idx:03d}"

def get_or_create_brand(brand_name: str) -> str:
    """Cerca o crea una marca su Supabase e restituisce l'ID."""
    brand_slug = slugify(brand_name)
    
    with httpx.Client(timeout=15.0, verify=False) as client:
        resp = client.get(f"{SUPABASE_REST_URL}/brands?slug=eq.{brand_slug}", headers=HEADERS)
        if resp.status_code == 200 and len(resp.json()) > 0:
            return resp.json()[0]["id"]
        
        new_brand = {
            "name": brand_name,
            "slug": brand_slug,
            "description": f"Collezione {brand_name}"
        }
        resp_post = client.post(f"{SUPABASE_REST_URL}/brands", json=new_brand, headers=HEADERS)
        
        if resp_post.status_code in (401, 403):
            raise PermissionError(
                "Errore 401 Unauthorized: Supabase ha bloccato l'inserimento.\n"
                "Assicurati di aver eseguito le POLICY su Supabase SQL Editor."
            )
            
        resp_post.raise_for_status()
        return resp_post.json()[0]["id"]

def import_photos():
    """Scansiona archivio_foto, copia le immagini in static e registra OGNI foto nel DB."""
    if not ARCHIVIO_DIR.exists():
        ARCHIVIO_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Cartella '{ARCHIVIO_DIR}' pronta.")
        return

    STATIC_DEST_DIR.mkdir(parents=True, exist_ok=True)

    extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
    processed_count = 0
    error_count = 0

    print("Inizio importazione di TUTTE le foto dall'archivio...")

    for root, dirs, files in os.walk(ARCHIVIO_DIR):
        valid_files = [f for f in sorted(files) if Path(f).suffix.lower() in extensions]
        if not valid_files:
            continue

        for idx, file in enumerate(valid_files, start=1):
            filepath = Path(root) / file
            relative_path = filepath.relative_to(ARCHIVIO_DIR)
            parts = relative_path.parts

            # Determinazione marca e modello dai livelli di cartelle
            if len(parts) >= 3:
                # archivio_foto / NB / 9060 / foto_013.jpeg
                brand_name = parts[0].strip()
                model_name = parts[1].strip()
            elif len(parts) == 2:
                # archivio_foto / Nike / Air Force 1.jpg
                brand_name = parts[0].strip()
                model_name = filepath.stem.strip()
            else:
                if " - " in filepath.stem:
                    brand_name, model_name = filepath.stem.split(" - ", 1)
                else:
                    brand_name = "Generale"
                    model_name = filepath.stem.strip()

            brand_name = brand_name.upper() if len(brand_name) <= 3 else brand_name.capitalize()
            model_name = model_name.capitalize()
            
            # Estrazione del numero dall'immagine (es. "013")
            num_code = extract_number(filepath.stem, idx)
            
            # FORMATO NOME RICHIESTO: Marca Modello-Numero (es. "NB 9060-013")
            shoe_display_name = f"{brand_name} {model_name}-{num_code}"
            
            # SLUG UNIVOCO PER LA SINGOLA FOTO
            shoe_slug = slugify(f"{brand_name}-{model_name}-{num_code}-{filepath.stem}")

            # Nome del file statico locale
            ext = filepath.suffix.lower()
            safe_filename = f"{slugify(brand_name)}_{slugify(model_name)}_{num_code}_{slugify(filepath.stem)}{ext}"
            dest_file = STATIC_DEST_DIR / safe_filename
            shutil.copy2(filepath, dest_file)

            image_url = f"{BASE_URL}/{safe_filename}"

            try:
                brand_id = get_or_create_brand(brand_name)

                with httpx.Client(timeout=15.0, verify=False) as client:
                    check_resp = client.get(
                        f"{SUPABASE_REST_URL}/shoes?brand_id=eq.{brand_id}&slug=eq.{shoe_slug}",
                        headers=HEADERS
                    )
                    
                    shoe_payload = {
                        "brand_id": brand_id,
                        "name": shoe_display_name,
                        "slug": shoe_slug,
                        "image_url": image_url,
                        "description": model_name  # Salva il Modello/Sottocartella (es. "9060")
                    }

                    if check_resp.status_code == 200 and len(check_resp.json()) > 0:
                        shoe_id = check_resp.json()[0]["id"]
                        client.patch(f"{SUPABASE_REST_URL}/shoes?id=eq.{shoe_id}", json=shoe_payload, headers=HEADERS)
                        print(f"Aggiornata: {shoe_display_name}")
                    else:
                        client.post(f"{SUPABASE_REST_URL}/shoes", json=shoe_payload, headers=HEADERS)
                        print(f"Inserita: {shoe_display_name}")

                processed_count += 1

            except PermissionError as pe:
                print(f"\n{pe}")
                return
            except Exception as e:
                error_count += 1
                print(f"Errore durante l'importazione di {filepath}: {e}")

    print(f"\nCompletata l'importazione! {processed_count} foto rimesse nel catalogo col nuovo formato nomi. (Errori: {error_count})")

if __name__ == "__main__":
    import_photos()
