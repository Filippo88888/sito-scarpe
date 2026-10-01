-- ==============================================================
-- SCHEMA SUPABASE: VETRINA SCARPE MINIMALE (SOLO 1 IMMAGINE)
-- ==============================================================

-- 1. TABELLA MARCHE (es. Nike, Adidas, Jordan, New Balance)
CREATE TABLE IF NOT EXISTS public.brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,             -- Per URL: /brands/nike
    logo_url TEXT,                         -- Logo della marca
    description TEXT,                      -- Breve descrizione della marca
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. TABELLA SCARPE / MODELLI (1 immagine per tipo di scarpa da vetrina)
-- Per ogni marca si hanno pagine/sezioni diverse in base allo slug del modello:
-- URL: /brands/[brand-slug]/[model-slug] (es. /brands/nike/air-force-1)
CREATE TABLE IF NOT EXISTS public.shoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES public.brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,                    -- Nome modello/tipo: es. "Air Force 1 '07"
    slug TEXT NOT NULL,                    -- Slug per la pagina: es. "air-force-1"
    image_url TEXT NOT NULL,               -- L'UNICA immagine da vetrina per questo tipo di scarpa
    description TEXT,                      -- Descrizione o dettagli di presentazione
    release_year INTEGER,                  -- Anno (opzionale, es. 1982)
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT unique_brand_shoe UNIQUE (brand_id, slug)
);

-- ==============================================================
-- INDICI PER PERFORMANCE (Ricerche rapide per slug e marca)
-- ==============================================================
CREATE INDEX IF NOT EXISTS idx_brands_slug ON public.brands(slug);
CREATE INDEX IF NOT EXISTS idx_shoes_brand_id ON public.shoes(brand_id);
CREATE INDEX IF NOT EXISTS idx_shoes_slug ON public.shoes(slug);

-- ==============================================================
-- ROW LEVEL SECURITY (RLS)
-- ==============================================================
ALTER TABLE public.brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shoes ENABLE ROW LEVEL SECURITY;

-- Lettura pubblica
CREATE POLICY "Public read brands" ON public.brands FOR SELECT USING (true);
CREATE POLICY "Public read shoes" ON public.shoes FOR SELECT USING (true);

-- Permessi per importazione foto
CREATE POLICY "Public insert brands" ON public.brands FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert shoes" ON public.shoes FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update shoes" ON public.shoes FOR UPDATE USING (true);
