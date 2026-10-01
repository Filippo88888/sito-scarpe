import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import PORT
from .routers import brands_router, shoes_router

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Sneaker Showcase API",
    description="Backend FastAPI per la visualizzazione e vetrina scarpe organizzate per marca e modello con Supabase.",
    version="1.0.0"
)

# Configurazione CORS per consentire le chiamate dal frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In sviluppo accetta tutte le origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestione File Statici per Immagini Locali
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Registrazione Router
app.include_router(brands_router)
app.include_router(shoes_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "Sneaker Showcase API is running",
        "docs": "/docs",
        "endpoints": {
            "all_brands": "/api/brands",
            "albums_with_shoes": "/api/brands/albums",
            "shoes_by_brand": "/api/brands/{brand_slug}/shoes",
            "all_shoes": "/api/shoes",
            "shoe_detail": "/api/shoes/{brand_slug}/{shoe_slug}"
        }
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=PORT, reload=True)
