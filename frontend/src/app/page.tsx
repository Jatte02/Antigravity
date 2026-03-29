"use client";

import { useEffect, useState } from "react";

// Estructura esperada desde el Backend
interface MercadoResumen {
  total_empresas: number;
  total_sectores: number;
  market_cap_total: number;
  avg_pe: number;
  top_gainers: Empresa[];
  top_losers: Empresa[];
  sectores: Sector[];
}

interface Empresa {
  symbol: string;
  short_name: string;
  sector: string;
  current_price: number;
}

interface Sector {
  sector: string;
  num_empresas: number;
  market_cap_total: number;
}

export default function Dashboard() {
  const [data, setData] = useState<MercadoResumen | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatMessage, setChatMessage] = useState("");
  const [chatResponse, setChatResponse] = useState<string | null>(null);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/mercado/resumen")
      .then((res) => res.json())
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error cargando dashboard:", error);
        setLoading(false);
      });
  }, []);

  const handleChat = async () => {
    if (!chatMessage) return;
    setChatLoading(true);
    setChatResponse(null);

    try {
      const resp = await fetch("http://localhost:8000/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatMessage }),
      });
      const chatData = await resp.json();
      setChatResponse(
        chatData.response || chatData.detail || "Error en el agente"
      );
    } catch (err) {
      setChatResponse("Fallo de conexión al enviar mensaje al agente.");
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center text-white font-sans">
        <div className="animate-pulse text-xl">Inicializando MarketSense...</div>
      </div>
    );
  }

  // Si falló en cargar /data, evita cracheos
  if (!data) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center text-white">
        Error conectando con la API Backend de MarketSense.
      </div>
    );
  }

  // @ts-ignore
  const formatMoney = (val) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(val);

  return (
    <div className="min-h-screen bg-[#09090b] text-gray-100 font-sans p-8 selection:bg-blue-500 selection:text-white">
      {/* HEADER */}
      <header className="mb-10 flex flex-col items-start gap-2 border-b border-gray-800 pb-6">
        <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          MarketSense
        </h1>
        <p className="text-gray-400 font-medium">Panel de Analista IA para S&P 500</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* COLUMNA IZQUIERDA: DASHBOARD */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          
          {/* Tarjetas Superiores */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-[#18181b] p-6 rounded-xl border border-gray-800 shadow-sm transition-transform hover:scale-[1.02]">
              <p className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-1">Empresas</p>
              <h2 className="text-3xl font-bold">{data.total_empresas}</h2>
            </div>
            <div className="bg-[#18181b] p-6 rounded-xl border border-gray-800 shadow-sm transition-transform hover:scale-[1.02]">
              <p className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-1">Cap. Bursátil</p>
              <h2 className="text-3xl font-bold">{formatMoney(data.market_cap_total)}</h2>
            </div>
            <div className="bg-[#18181b] p-6 rounded-xl border border-gray-800 shadow-sm transition-transform hover:scale-[1.02]">
              <p className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-1">Razón P/E (Media)</p>
              <h2 className="text-3xl font-bold">{data.avg_pe?.toFixed(2)}x</h2>
            </div>
             <div className="bg-[#18181b] p-6 rounded-xl border border-gray-800 shadow-sm transition-transform hover:scale-[1.02]">
              <p className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-1">Sectores</p>
              <h2 className="text-3xl font-bold">{data.total_sectores}</h2>
            </div>
          </div>

          {/* Grilla Doble: Tops */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-[#18181b] p-6 rounded-xl border border-gray-800">
              <h3 className="text-xl font-bold mb-4 text-emerald-400 flex items-center gap-2">
                <span className="text-2xl">↗</span> Top Crecimiento (%)
              </h3>
              <ul className="space-y-4">
                {data.top_gainers?.slice(0, 5).map((e, idx) => (
                  <li key={idx} className="flex justify-between items-center group">
                    <div className="flex items-center gap-3">
                      <span className="font-mono bg-emerald-900/40 text-emerald-400 px-2 flex items-center h-8 rounded shrink-0 font-bold border border-emerald-500/20">{e.symbol}</span>
                      <p className="text-sm text-gray-300 truncate w-32 group-hover:text-white transition-colors">{e.short_name}</p>
                    </div>
                    <span className="font-semibold text-white tracking-wide">${e.current_price?.toFixed(2)}</span>
                  </li>
                ))}
            </ul>
            </div>

            <div className="bg-[#18181b] p-6 rounded-xl border border-gray-800">
              <h3 className="text-xl font-bold mb-4 text-red-400 flex items-center gap-2">
                 <span className="text-2xl">↘</span> Mayor Caída (%)
              </h3>
              <ul className="space-y-4">
                  {data.top_losers?.slice(0, 5).map((e, idx) => (
                  <li key={idx} className="flex justify-between items-center group">
                    <div className="flex items-center gap-3">
                      <span className="font-mono bg-red-900/40 text-red-500 px-2 flex items-center h-8 rounded shrink-0 font-bold border border-red-500/20">{e.symbol}</span>
                      <p className="text-sm text-gray-300 truncate w-32 group-hover:text-white transition-colors">{e.short_name}</p>
                    </div>
                    <span className="font-semibold text-white tracking-wide">${e.current_price?.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
           {/* Tabla Sectores */}
           <div className="bg-[#18181b] overflow-hidden rounded-xl border border-gray-800">
             <div className="p-6 border-b border-gray-800">
                <h3 className="text-xl font-bold text-gray-100">Market Cap por Sectores Principales</h3>
             </div>
             <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-[#27272a] text-gray-300 uppercase font-mono text-xs tracking-wider">
                  <tr>
                    <th className="py-4 pl-6 font-semibold">Sector</th>
                    <th className="py-4 font-semibold text-right">Compañías</th>
                    <th className="py-4 pr-6 text-right font-semibold">Valor Capitalización</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {data.sectores?.map((sect, i) => (
                    <tr key={i} className="hover:bg-white/5 transition-colors">
                      <td className="py-4 pl-6 text-emerald-100 font-medium">{sect.sector}</td>
                      <td className="py-4 text-right pr-2 text-gray-400">{sect.num_empresas}</td>
                      <td className="py-4 pr-6 text-right text-gray-200">{formatMoney(sect.market_cap_total)}</td>
                    </tr>
                  ))}
                </tbody>
             </table>
           </div>
        </div>

        {/* COLUMNA DERECHA: CHAT CON AGENTE */}
        <div className="bg-gradient-to-b from-[#18181b] to-[#121215] border border-gray-800 rounded-xl p-6 flex flex-col shadow-2xl relative overflow-hidden group">
           {/* "Glow" Decorativo */}
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <div className="w-32 h-32 bg-blue-500 rounded-full blur-[80px]"></div>
          </div>
          
          <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400 mb-2">Agente ReAct</h2>
          <p className="text-sm text-gray-400 mb-6 border-b border-gray-800 pb-4">Conectado a LangGraph & PostgreSQL. Ingresa GEMINI_API_KEY en .env para respuestas reales.</p>
          
          <div className="flex-1 min-h-[300px] mb-6 overflow-y-auto pr-2 custom-scrollbar flex flex-col justify-end space-y-4">
             {chatResponse ? (
               <div className="bg-blue-900/20 border border-blue-500/20 p-4 rounded-xl text-blue-100 text-sm leading-relaxed whitespace-pre-wrap break-words">
                  <span className="font-bold text-blue-400 mb-2 block text-xs tracking-wider uppercase">MarketSense-AI dice:</span>
                  {chatResponse}
               </div>
             ) : (
                <div className="m-auto text-gray-600 text-sm flex flex-col items-center gap-3">
                   <div className="w-12 h-12 bg-gray-800/50 rounded-full flex items-center justify-center border border-gray-700">🤖</div>
                   <p className="text-center w-48">Tu asistente IA LangGraph está en espera.</p>
                </div>
             )}
              {chatLoading && (
               <div className="text-emerald-400 text-xs font-mono animate-pulse mr-auto">
                 [ Pensando con Bedrock e invocando SQL Tools... ]
               </div>
             )}
          </div>

          <div className="relative">
            <textarea
              className="w-full bg-[#09090b] border border-gray-700 text-white rounded-xl p-4 pr-16 text-sm resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-medium placeholder-gray-600"
              rows={3}
              placeholder="Ej: Muestra el correlation_rate de AAPL y MSFT..."
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleChat())}
            ></textarea>
            <button 
              onClick={handleChat}
              disabled={chatLoading}
              className="absolute bottom-4 right-4 bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-lg transition-colors hover:shadow-lg disabled:opacity-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
