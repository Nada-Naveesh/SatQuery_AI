import React from 'react';
import { AnalysisResult } from '../types';

interface ResultCardProps {
  result?: AnalysisResult;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const confPct = result ? Math.round(result.confidence_score * 100) : 0;

  return (
    <div className="border border-space-700 bg-space-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Grounded Operational Answer
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-[11px] text-slate-400">Confidence:</span>
          <div className="w-20 bg-space-900 rounded-full h-2 overflow-hidden border border-space-700">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${confPct}%` }}
            />
          </div>
          <span className="text-xs font-mono font-bold text-emerald-400">
            {result ? `${confPct}%` : '--%'}
          </span>
        </div>
      </div>

      <div className="p-3 bg-space-900/70 border border-space-700 rounded-lg text-xs leading-relaxed text-slate-200">
        {result?.text_answer ||
          'Run an analysis to inspect grounded textual reasoning and spatial observations.'}
      </div>

      {result?.summary_bullet_points && result.summary_bullet_points.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
            Telemetry & Grounded Observations
          </span>
          <ul className="text-[11px] text-slate-300 space-y-1 list-disc list-inside">
            {result.summary_bullet_points.map((b, idx) => (
              <li key={idx}>{b}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
