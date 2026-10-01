import React, { useState, useEffect, useMemo } from 'react';
import { Search, Link as LinkIcon, Check, X, Maximize2, Layers, Tag } from 'lucide-react';

export default function App() {
  const [shoes, setShoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('ALL');
  const [selectedModel, setSelectedModel] = useState('ALL');
  const [enlargedShoe, setEnlargedShoe] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  // Caricamento scarpe dall'API FastAPI
  useEffect(() => {
    fetchShoes();
  }, []);

  const fetchShoes = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/shoes');
      const data = await res.json();
      setShoes(data);

      // Apri da hash se presente nell'URL
      const hash = window.location.hash.replace('#shoe-', '').replace('#', '');
      if (hash) {
        const found = data.find((s) => s.slug === hash || s.id === hash);
        if (found) {
          setEnlargedShoe(found);
        }
      }
    } catch (err) {
      console.error('Errore nel caricamento scarpe:', err);
    } finally {
      setLoading(false);
    }
  };

  // Elenco delle marche uniche (mostra solo marche con almeno 1 foto)
  const brands = useMemo(() => {
    const brandCounts = {};
    shoes.forEach((item) => {
      const bName = item.brands?.name;
      if (bName) {
        brandCounts[bName] = (brandCounts[bName] || 0) + 1;
      }
    });
    return Object.keys(brandCounts).sort();
  }, [shoes]);

  // Elenco dei modelli (sottocartelle) filtrati in base alla marca selezionata
  const availableModels = useMemo(() => {
    let filtered = shoes;
    if (selectedBrand !== 'ALL') {
      filtered = shoes.filter((item) => item.brands?.name === selectedBrand);
    }
    const modelSet = new Set();
    filtered.forEach((item) => {
      const modelName = item.description || item.name.split(' ')[1]?.split('-')[0];
      if (modelName) modelSet.add(modelName);
    });
    return Array.from(modelSet).sort();
  }, [shoes, selectedBrand]);

  // Reset del modello selezionato quando si cambia marca
  const handleSelectBrand = (brand) => {
    setSelectedBrand(brand);
    setSelectedModel('ALL');
  };

  // Apertura e Chiusura Lightbox Modal
  const handleOpenLightbox = (shoe) => {
    setEnlargedShoe(shoe);
    window.history.pushState(null, '', `#shoe-${shoe.slug}`);
  };

  const handleCloseLightbox = () => {
    setEnlargedShoe(null);
    window.history.pushState(null, '', window.location.pathname);
  };

  // Copia del link diretto
  const copyShoeLink = (e, shoe) => {
    e.stopPropagation();
    const directLink = `${window.location.origin}${window.location.pathname}#shoe-${shoe.slug}`;

    navigator.clipboard.writeText(directLink).then(() => {
      setCopiedId(shoe.id);
      setTimeout(() => setCopiedId(null), 2500);
    });
  };

  // Filtraggio finale delle scarpe per Marca, Modello e Ricerca
  const filteredShoes = useMemo(() => {
    return shoes.filter((shoe) => {
      const matchesSearch = shoe.name.toLowerCase().includes(search.toLowerCase());
      const matchesBrand = selectedBrand === 'ALL' || shoe.brands?.name === selectedBrand;
      
      const shoeModel = shoe.description || shoe.name.split(' ')[1]?.split('-')[0];
      const matchesModel = selectedModel === 'ALL' || shoeModel === selectedModel;

      return matchesSearch && matchesBrand && matchesModel;
    });
  }, [shoes, search, selectedBrand, selectedModel]);

  return (
    <div className="min-h-screen bg-[#0D0D0E] text-gray-100 flex flex-col">
      {/* Toast Notifica Copia Link */}
      {copiedId && (
        <div className="fixed top-6 right-6 z-50 bg-[#FF5500] text-white px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3 animate-bounce border border-orange-400 font-semibold text-sm">
          <Check className="w-5 h-5" />
          Link scarpa copiato negli appunti!
        </div>
      )}

      {/* HEADER PRINCIPALE */}
      <header className="sticky top-0 z-30 bg-[#0D0D0E]/95 backdrop-blur-md border-b border-[#26262A] py-4 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => { setSelectedBrand('ALL'); setSelectedModel('ALL'); setSearch(''); }}
          >
            <div className="w-10 h-10 rounded-xl bg-[#FF5500] flex items-center justify-center text-white font-extrabold text-xl shadow-lg shadow-orange-950/40">
              S
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-wider text-white uppercase flex items-center gap-2">
                VETRINA <span className="text-[#FF5500]">SCARPE</span>
              </h1>
            </div>
          </div>

          {/* BARRA DI RICERCA */}
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cerca per modello o codice (es. 9060-001)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#161618] text-white text-sm pl-10 pr-4 py-2.5 rounded-xl border border-[#26262A] focus:outline-none focus:border-[#FF5500] transition-colors placeholder:text-gray-500"
            />
          </div>
        </div>
      </header>

      {/* CONTENUTO PRINCIPALE */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6">

        {/* 1. FILTRI PER MARCA (Solo marche con foto presenti) */}
        {brands.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
              <span className="text-xs uppercase font-bold text-gray-400 mr-1 flex items-center gap-1">
                Marca:
              </span>
              <button
                onClick={() => handleSelectBrand('ALL')}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold uppercase transition-all whitespace-nowrap ${
                  selectedBrand === 'ALL'
                    ? 'bg-[#FF5500] text-white shadow-md shadow-orange-900/30'
                    : 'bg-[#161618] text-gray-400 border border-[#26262A] hover:border-gray-600 hover:text-white'
                }`}
              >
                TUTTE ({shoes.length})
              </button>
              {brands.map((brand) => {
                const count = shoes.filter((s) => s.brands?.name === brand).length;
                return (
                  <button
                    key={brand}
                    onClick={() => handleSelectBrand(brand)}
                    className={`px-4 py-2 rounded-xl text-xs font-extrabold uppercase transition-all whitespace-nowrap ${
                      selectedBrand === brand
                        ? 'bg-[#FF5500] text-white shadow-md shadow-orange-900/30'
                        : 'bg-[#161618] text-gray-400 border border-[#26262A] hover:border-gray-600 hover:text-white'
                    }`}
                  >
                    {brand} ({count})
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* 2. SOTTOPAGINE PER MODELLO / SOTTOCARTELLA (senza prefisso "Modello") */}
        {availableModels.length > 0 && (
          <div className="mb-6 bg-[#141416] p-4 rounded-2xl border border-[#26262A]">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-orange-400 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-4 h-4" />
                Sottopagine {selectedBrand !== 'ALL' ? `(${selectedBrand})` : ''}:
              </span>
              {selectedModel !== 'ALL' && (
                <button
                  onClick={() => setSelectedModel('ALL')}
                  className="text-xs text-gray-400 hover:text-orange-400 underline font-medium"
                >
                  Mostra tutti
                </button>
              )}
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => setSelectedModel('ALL')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  selectedModel === 'ALL'
                    ? 'bg-white text-black font-extrabold shadow-sm'
                    : 'bg-[#212124] text-gray-400 hover:bg-[#2A2A2E] hover:text-white border border-[#2D2D32]'
                }`}
              >
                Tutti ({shoes.filter(s => selectedBrand === 'ALL' || s.brands?.name === selectedBrand).length})
              </button>
              
              {availableModels.map((model) => {
                const count = shoes.filter((s) => {
                  const m = s.description || s.name.split(' ')[1]?.split('-')[0];
                  const matchB = selectedBrand === 'ALL' || s.brands?.name === selectedBrand;
                  return matchB && m === model;
                }).length;

                return (
                  <button
                    key={model}
                    onClick={() => setSelectedModel(model)}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                      selectedModel === model
                        ? 'bg-[#FF5500] text-white shadow-md border border-orange-400'
                        : 'bg-[#212124] text-gray-300 hover:bg-[#FF5500]/20 hover:text-orange-400 hover:border-[#FF5500]/40 border border-[#2D2D32]'
                    }`}
                  >
                    <span>{model}</span>
                    <span className="opacity-75 bg-black/30 px-1.5 py-0.5 rounded text-[10px] font-mono">
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* TITOLO SEZIONE / SOTTOPAGINA CORRENTE */}
        <div className="flex items-center justify-between mb-6 pb-2 border-b border-[#26262A]/60">
          <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
            <Tag className="w-5 h-5 text-[#FF5500]" />
            {selectedModel !== 'ALL'
              ? `${selectedBrand !== 'ALL' ? selectedBrand : ''} ${selectedModel}`
              : selectedBrand !== 'ALL'
              ? `Collezione: ${selectedBrand}`
              : 'Tutte le Foto'}
            <span className="text-xs font-normal text-gray-400 bg-[#161618] px-2.5 py-1 rounded-full border border-[#26262A]">
              {filteredShoes.length} foto
            </span>
          </h2>
        </div>

        {/* STATO CARICAMENTO */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 text-gray-500 gap-3">
            <div className="w-8 h-8 border-4 border-[#FF5500] border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm">Caricamento vetrina scarpe...</p>
          </div>
        ) : filteredShoes.length === 0 ? (
          <div className="text-center py-20 bg-[#161618] rounded-2xl border border-[#26262A]">
            <p className="text-gray-400 font-medium text-lg">Nessuna scarpa trovata</p>
            <p className="text-xs text-gray-500 mt-1">Seleziona una marca o un sottomodello differente.</p>
          </div>
        ) : (
          /* GRIGLIA DI CARDS SCARPE */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredShoes.map((shoe) => (
              <div
                key={shoe.id}
                onClick={() => handleOpenLightbox(shoe)}
                className="group relative bg-[#161618] rounded-2xl border border-[#26262A] overflow-hidden hover:border-[#FF5500] transition-all duration-300 flex flex-col justify-between cursor-pointer shadow-lg hover:shadow-orange-950/20"
              >
                {/* CONTENITORE IMMAGINE */}
                <div className="relative aspect-square w-full overflow-hidden bg-[#09090A] flex items-center justify-center p-4">
                  <img
                    src={shoe.image_url}
                    alt={shoe.name}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500 ease-out"
                    loading="lazy"
                  />

                  {/* Overlay ingrandisci */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <span className="bg-[#FF5500] text-white p-3 rounded-full shadow-lg transform group-hover:scale-110 transition-transform">
                      <Maximize2 className="w-5 h-5" />
                    </span>
                  </div>
                </div>

                {/* INFO NOME MARCA MODELLO-NUMERO E BOTTONE COPIA LINK */}
                <div className="p-4 bg-[#161618] flex items-center justify-between gap-3 border-t border-[#26262A]/60">
                  <div className="truncate">
                    {/* FORMATO NOME RICHIESTO: NB 9060-001 */}
                    <h3 className="font-extrabold text-white text-base truncate group-hover:text-[#FF5500] transition-colors">
                      {shoe.name}
                    </h3>
                    <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase">
                      {shoe.brands?.name || 'Vetrina'}
                    </span>
                  </div>

                  {/* BOTTONE COPIA LINK */}
                  <button
                    onClick={(e) => copyShoeLink(e, shoe)}
                    title="Copia link diretto scarpa"
                    className={`p-2.5 rounded-xl border transition-all flex items-center gap-1.5 text-xs font-bold ${
                      copiedId === shoe.id
                        ? 'bg-green-600 text-white border-green-500'
                        : 'bg-[#212124] text-gray-300 border-[#2D2D32] hover:bg-[#FF5500] hover:text-white hover:border-[#FF5500]'
                    }`}
                  >
                    {copiedId === shoe.id ? (
                      <>
                        <Check className="w-4 h-4" />
                        <span className="hidden sm:inline">Copiato</span>
                      </>
                    ) : (
                      <>
                        <LinkIcon className="w-4 h-4" />
                        <span className="hidden sm:inline">Copia Link</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* LIGHTBOX MODAL INGRANDIMENTO */}
      {enlargedShoe && (
        <div
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-xl flex items-center justify-center p-4 sm:p-8 animate-fade-in"
          onClick={handleCloseLightbox}
        >
          <div
            className="relative max-w-5xl w-full max-h-[90vh] bg-[#161618] border border-[#26262A] rounded-3xl overflow-hidden flex flex-col shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header Modal */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#26262A] bg-[#0D0D0E]/80">
              <div className="flex items-center gap-3">
                <span className="bg-[#FF5500] text-white px-3 py-1 rounded-lg text-xs font-black uppercase tracking-wider">
                  {enlargedShoe.brands?.name || 'Vetrina'}
                </span>
                <h2 className="text-lg font-extrabold text-white truncate">{enlargedShoe.name}</h2>
              </div>

              <div className="flex items-center gap-3">
                {/* Bottone Copia Link nel Modal */}
                <button
                  onClick={(e) => copyShoeLink(e, enlargedShoe)}
                  className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all ${
                    copiedId === enlargedShoe.id
                      ? 'bg-green-600 text-white border-green-500'
                      : 'bg-[#FF5500] text-white border-orange-500 hover:bg-orange-600'
                  }`}
                >
                  {copiedId === enlargedShoe.id ? (
                    <>
                      <Check className="w-4 h-4" />
                      Link Copiato!
                    </>
                  ) : (
                    <>
                      <LinkIcon className="w-4 h-4" />
                      Copia Link
                    </>
                  )}
                </button>

                {/* Bottone Chiudi (X) */}
                <button
                  onClick={handleCloseLightbox}
                  className="p-2 rounded-full bg-[#26262A] text-gray-300 hover:text-white hover:bg-[#FF5500] transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Immagine Ingrandita */}
            <div className="flex-1 bg-[#09090A] p-6 flex items-center justify-center min-h-[350px] overflow-hidden">
              <img
                src={enlargedShoe.image_url}
                alt={enlargedShoe.name}
                className="max-h-[70vh] w-auto object-contain rounded-xl drop-shadow-2xl select-none"
              />
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="border-t border-[#26262A] py-6 text-center text-xs text-gray-500 mt-12 bg-[#0D0D0E]">
        <p>Vetrina Scarpe &copy; {new Date().getFullYear()} — Soluzione Minimalista e Veloce</p>
      </footer>
    </div>
  );
}
