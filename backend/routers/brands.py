from typing import List
from fastapi import APIRouter
from ..database import SupabaseService
from ..schemas.shoe import BrandOut, AlbumOut, ShoeOut

router = APIRouter(prefix="/api/brands", tags=["Marche & Album"])

@router.get("", response_model=List[BrandOut], summary="Lista di tutte le marche")
async def list_brands():
    """Restituisce l'elenco di tutte le marche disponibili."""
    return await SupabaseService.get_all_brands()

@router.get("/albums", response_model=List[AlbumOut], summary="Album completi con scarpe e foto di anteprima")
async def list_albums():
    """
    Restituisce le marche organizzate come album di scarpe.
    Include per ogni marca la lista completa di scarpe con l'immagine di vetrina.
    """
    return await SupabaseService.get_albums_with_shoes()

@router.get("/{brand_slug}", response_model=BrandOut, summary="Dettagli di una singola marca")
async def get_brand(brand_slug: str):
    """Restituisce i dati della marca specificata tramite slug."""
    return await SupabaseService.get_brand_by_slug(brand_slug)

@router.get("/{brand_slug}/shoes", response_model=List[ShoeOut], summary="Tutte le scarpe dell'album di una marca")
async def list_brand_shoes(brand_slug: str):
    """Restituisce tutte le scarpe appartenenti alla marca/sezione indicata."""
    return await SupabaseService.get_shoes_by_brand(brand_slug)
