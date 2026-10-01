from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class BrandOut(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class ShoeOut(BaseModel):
    id: str
    brand_id: str
    name: str
    slug: str
    image_url: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    created_at: Optional[datetime] = None
    brands: Optional[BrandOut] = None

class ShoeDetailOut(ShoeOut):
    pass

class AlbumOut(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    total_shoes: int
    cover_preview: Optional[str] = None
    shoes: List[ShoeOut] = []
