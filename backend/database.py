from typing import Any, Dict, List, Optional
import httpx
from fastapi import HTTPException
from .config import SUPABASE_REST_URL, SUPABASE_KEY

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

async def fetch_from_supabase(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    if not SUPABASE_REST_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Configurazione Supabase mancante nel file .env")
    
    url = f"{SUPABASE_REST_URL}/{endpoint}"
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        try:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Errore Supabase: {exc.response.text}"
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Errore di connessione: {str(exc)}")

class SupabaseService:
    @staticmethod
    async def get_all_brands() -> List[Dict[str, Any]]:
        """Recupera tutte le marche disponibili (gli album delle scarpe)."""
        return await fetch_from_supabase("brands", params={"select": "*", "order": "name.asc"})

    @staticmethod
    async def get_brand_by_slug(brand_slug: str) -> Dict[str, Any]:
        """Recupera i dettagli di una singola marca tramite il suo slug."""
        data = await fetch_from_supabase("brands", params={"slug": f"eq.{brand_slug}", "select": "*"})
        if not data:
            raise HTTPException(status_code=404, detail=f"Marca '{brand_slug}' non trovata")
        return data[0]

    @staticmethod
    async def get_shoes_by_brand(brand_slug: str) -> List[Dict[str, Any]]:
        """Recupera tutte le scarpe dell'album di una specifica marca."""
        brand = await SupabaseService.get_brand_by_slug(brand_slug)
        brand_id = brand["id"]
        
        shoes = await fetch_from_supabase(
            "shoes",
            params={
                "brand_id": f"eq.{brand_id}",
                "select": "*",
                "order": "created_at.desc"
            }
        )
        return shoes

    @staticmethod
    async def get_all_shoes(search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recupera tutte le scarpe con i dati della marca associata."""
        params = {
            "select": "*,brands(id,name,slug,logo_url)",
            "order": "created_at.desc"
        }
        if search:
            params["name"] = f"ilike.*{search}*"
        return await fetch_from_supabase("shoes", params=params)

    @staticmethod
    async def get_shoe_detail(brand_slug: str, shoe_slug: str) -> Dict[str, Any]:
        """Recupera la scheda vetrina di una specifica scarpa dato il brand e lo slug del modello."""
        brand = await SupabaseService.get_brand_by_slug(brand_slug)
        brand_id = brand["id"]
        
        data = await fetch_from_supabase(
            "shoes",
            params={
                "brand_id": f"eq.{brand_id}",
                "slug": f"eq.{shoe_slug}",
                "select": "*,brands(id,name,slug,logo_url,description)"
            }
        )
        if not data:
            raise HTTPException(status_code=404, detail=f"Modello '{shoe_slug}' non trovato per la marca '{brand_slug}'")
        return data[0]

    @staticmethod
    async def get_albums_with_shoes() -> List[Dict[str, Any]]:
        """Restituisce le marche raggruppate come album con le relative foto da vetrina."""
        brands = await SupabaseService.get_all_brands()
        shoes = await fetch_from_supabase("shoes", params={"select": "*", "order": "created_at.desc"})
        
        # Raggruppa le scarpe per brand_id
        shoes_by_brand: Dict[str, List[Dict[str, Any]]] = {}
        for shoe in shoes:
            b_id = shoe.get("brand_id")
            if b_id:
                shoes_by_brand.setdefault(b_id, []).append(shoe)
        
        result = []
        for brand in brands:
            brand_shoes = shoes_by_brand.get(brand["id"], [])
            result.append({
                "id": brand["id"],
                "name": brand["name"],
                "slug": brand["slug"],
                "logo_url": brand.get("logo_url"),
                "description": brand.get("description"),
                "total_shoes": len(brand_shoes),
                "cover_preview": brand_shoes[0]["image_url"] if brand_shoes else None,
                "shoes": brand_shoes
            })
        return result
