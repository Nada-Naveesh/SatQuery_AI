import React from 'react';

interface QueryPanelProps {
  query: string;
  setQuery: (q: string) => void;
  onExecute: () => void;
  isLoading: boolean;
}

export const QueryPanel: React.FC<QueryPanelProps> = ({
  query,
  setQuery,
  onExecute,
  isLoading,
}) => {
  const suggestions = [
    { label: '🔄 What Changed?', text: 'What changed here between 2025 and 2026?' },
    { label: '🏢 Where Buildings?', text: 'Where are the buildings in this image?' },
    { label: '💧 Water Bodies', text: 'Show me the water bodies.' },
    { label: '🌾 Submerged Farmlands', text: 'Identify the submerged agricultural parcels and highlight their spatial boundaries.' },
  ];

  return (
    <div className="border border-space-700 bg-space-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Natural Language Query
        </label>
        <span className="text-[10px] text-cyan-400 font-medium">Plain English &bull; Auto-Routed</span>
      </div>

      <textarea
        rows={3}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="E.g. What changed here between 2025 and 2026? or Where are the buildings?"
        className="w-full bg-space-900 border border-space-600 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 resize-none font-medium"
      />

      <div className="flex flex-wrap gap-1.5">
        {suggestions.map((s, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => setQuery(s.text)}
            className="text-[10px] bg-space-900 border border-space-700 hover:border-slate-500 px-2 py-1 rounded text-slate-300 transition"
          >
            {s.label}
          </button>
        ))}
      </div>

      <button
        type="button"
        onClick={onExecute}
        disabled={isLoading || !query.trim()}
        className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-cyan-600/30"
      >
        {isLoading ? (
          <span>Analyzing satellite imagery and preparing answer...</span>
        ) : (
          <span>Analyze Satellite Images</span>
        )}
      </button>
    </div>
  );
};
