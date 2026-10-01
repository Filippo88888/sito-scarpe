from typing import List, Optional
from fastapi import APIRouter, Query
from ..database import SupabaseService
from ..schemas.shoe import ShoeOut, ShoeDetailOut

router = APIRouter(prefix="/api/shoes", tags=["Scarpe / Vetrina"])

@router.get("", response_model=List[ShoeOut], summary="Catalogo generale scarpe")
async def list_all_shoes(search: Optional[str] = Query(None, description="Cerca per nome modello")):
    """Restituisce tutte le scarpe registrate, con filtro di ricerca opzionale."""
    return await SupabaseService.get_all_shoes(search=search)

@router.get("/{brand_slug}/{shoe_slug}", response_model=ShoeDetailOut, summary="Scheda vetrina della singola scarpa")
async def get_shoe_detail(brand_slug: str, shoe_slug: str):
    """
    Restituisce la scheda completa da vetrina di una specifica scarpa 
    dato il brand e lo slug del modello.
    """
    return await SupabaseService.get_shoe_detail(brand_slug, shoe_slug)
