import React, { useState } from 'react';
import { ExecutionTrace as TraceType } from '../types';

interface ExecutionTraceProps {
  trace?: TraceType;
}

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ trace }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-space-700 bg-space-800 rounded-xl p-4 shadow-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Auditable Execution Trace
          </span>
          <span className="text-[10px] font-mono text-slate-500">
            {trace ? `ID: ${trace.trace_id}` : 'No execution logged'}
          </span>
        </div>
        <span className="text-xs text-slate-400">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && trace && (
        <div className="mt-3 pt-3 border-t border-space-700 text-xs space-y-3 font-mono">
          <div className="bg-space-900 p-2.5 rounded border border-space-700 text-[11px] space-y-1">
            <div className="text-slate-400">
              <b className="text-slate-200">Router Reasoning: </b>
              <span className="text-cyan-300">{trace.router_reasoning}</span>
            </div>
            <div className="text-slate-400">
              <b className="text-slate-200">Total Latency: </b>
              <span className="text-emerald-400">{trace.total_execution_time_ms} ms</span>
            </div>
          </div>

          <div>
            <span className="text-[10px] uppercase text-slate-400 font-sans font-bold">
              Specialist Tool Telemetry
            </span>
            <div className="mt-1.5 space-y-1.5">
              {trace.tools_executed.map((t, idx) => (
                <div
                  key={idx}
                  className="p-2 rounded bg-space-800 border border-space-700 flex justify-between items-center text-[11px]"
                >
                  <div>
                    <b className="text-cyan-400">{t.tool_name}</b>
                    <span className="text-slate-500 block text-[9px]">{t.model_checkpoint}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-emerald-400">{t.execution_time_ms} ms</span>
                    <span className="text-slate-500 block text-[9px]">
                      Conf: {(t.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
