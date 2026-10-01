-- ==============================================================
-- DATI DI PROVA (SEED DATA) - VETRINA SCARPE MINIMALE
-- ==============================================================

-- 1. Marche
INSERT INTO public.brands (id, name, slug, logo_url, description)
VALUES 
    (
        '11111111-1111-1111-1111-111111111111',
        'Nike',
        'nike',
        'https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg',
        'Leader mondiale dello sportswear e della sneaker culture.'
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'Adidas',
        'adidas',
        'https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg',
        'Icona dello stile sportivo con le inconfondibili tre strisce.'
    )
ON CONFLICT (slug) DO NOTHING;

-- 2. Tipi di scarpe / Modelli (1 immagine vetrina per ciascuno, nessun prezzo, nessuna variante)
INSERT INTO public.shoes (brand_id, name, slug, image_url, description, release_year)
VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'Air Force 1',
        'air-force-1',
        'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=1000&q=80',
        'La classica silhouette da basket del 1982 che ha definito lo streetwear.',
        1982
    ),
    (
        '11111111-1111-1111-1111-111111111111',
        'Dunk Low',
        'dunk-low',
        'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=1000&q=80',
        'Nata sui parquet universitari e diventata punto di riferimento nello skate e nel lifestyle.',
        1985
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'Samba OG',
        'samba-og',
        'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?auto=format&fit=crop&w=1000&q=80',
        'Creata originariamente per il calcio e oggi regina dello stile rétro.',
        1950
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'Gazelle',
        'gazelle',
        'https://images.unsplash.com/photo-1520256862855-398228c41684?auto=format&fit=crop&w=1000&q=80',
        'Design minimalista in pelle scamosciata che attraversa le generazioni.',
        1966
    )
ON CONFLICT (brand_id, slug) DO NOTHING;
