import React, { useState } from 'react';
import Head from 'next/head';
import { executeAnalysis, getPdfReportUrl } from '../api/client';
import { AnalysisResponse } from '../types';

export default function DemoPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AnalysisResponse | null>(null);

  const steps = [
    {
      step: 1,
      name: 'Single-Image Flood VQA & Grounding',
      scenarioId: 'scenario_1_flood',
      query: 'Identify the submerged agricultural parcels and highlight their spatial boundaries.',
      image: '/static/samples/flood_sentinel2_optical.png',
      badge: 'Single Optical (Sentinel-2)',
      talkingPoint: 'Demonstrates spatial grounding over optical reflectance without hallucinations.'
    },
    {
      step: 2,
      name: 'Bi-Temporal Urban Sprawl (CDVQA)',
      scenarioId: 'scenario_2_urban',
      query: 'What major infrastructure changes occurred between these two acquisition dates?',
      image: '/static/samples/urban_t2_2024.png',
      badge: 'Temporal Pair (2022 vs 2024)',
      talkingPoint: 'Computes pixel-level difference tensor and natural-language change reasoning.'
    },
    {
      step: 3,
      name: 'All-Weather Optical-SAR Cloud Penetration',
      scenarioId: 'scenario_3_optical_sar',
      query: 'Penetrate cloud cover to map industrial storage tanks and coastal water bodies.',
      image: '/static/samples/co_registered_optical_cloudy.png',
      badge: 'Cartosat-2S + RISAT SAR',
      talkingPoint: 'Fuses optical cues with C-band radar backscatter to pierce dense monsoon clouds.'
    }
  ];

  const activeDemo = steps[currentStep - 1];

  const handleRunCurrentStep = async () => {
    setLoading(true);
    try {
      const res = await executeAnalysis(activeDemo.query, undefined, activeDemo.scenarioId);
      setResponse(res);
    } catch (e: any) {
      alert(`Demo execution failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-space-900 text-slate-100 flex flex-col font-sans">
      <Head>
        <title>SIH 2026 Live Demo — SatQuery AI (PS 26167)</title>
      </Head>

      <header className="border-b border-space-700 bg-space-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-base font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            SatQuery AI &bull; ISRO 2-3 Minute Hackathon Demo Mode
          </h1>
          <p className="text-xs text-slate-400">Problem Statement 26167 &bull; Space Technology</p>
        </div>

        <div className="flex items-center space-x-2">
          {steps.map((s) => (
            <button
              key={s.step}
              onClick={() => {
                setCurrentStep(s.step);
                setResponse(null);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                currentStep === s.step
                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30'
                  : 'bg-space-800 text-slate-400 hover:text-white border border-space-700'
              }`}
            >
              Demo {s.step}
            </button>
          ))}
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        {/* Left: Script & Controls */}
        <div className="space-y-4">
          <div className="bg-space-800 border border-space-700 rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">
              Stage {currentStep} of 3
            </span>
            <h2 className="text-sm font-bold text-white mt-0.5">{activeDemo.name}</h2>
            <span className="inline-block mt-1 text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono">
              {activeDemo.badge}
            </span>
            <div className="mt-3 p-2.5 rounded bg-space-900 border border-space-700 text-xs text-slate-300">
              <b className="text-amber-300">Judge Pitch Point:</b> {activeDemo.talkingPoint}
            </div>
          </div>

          <div className="bg-space-800 border border-space-700 rounded-xl p-4 space-y-2">
            <label className="text-xs font-bold text-slate-400 uppercase">Live Prompt to Run</label>
            <div className="p-3 rounded-lg bg-space-900 border border-space-700 text-xs font-medium text-slate-200">
              "{activeDemo.query}"
            </div>

            <button
              onClick={handleRunCurrentStep}
              disabled={loading}
              className="w-full mt-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-2.5 px-4 rounded-lg text-xs shadow-lg transition"
            >
              {loading ? 'Executing Specialist AI Pipeline...' : 'Run Live Inference on Stage ' + currentStep}
            </button>
          </div>

          {response && (
            <div className="bg-space-800 border border-space-700 rounded-xl p-4 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-300 uppercase">Grounded Response</span>
                <span className="text-xs font-mono font-bold text-emerald-400">
                  Confidence: {Math.round(response.result.confidence_score * 100)}%
                </span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed bg-space-900 p-3 rounded-lg border border-space-700">
                {response.result.text_answer}
              </p>
              <button
                onClick={() => window.open(getPdfReportUrl(response.execution_trace.trace_id), '_blank')}
                className="w-full bg-space-700 hover:bg-space-600 text-white text-xs font-medium py-2 rounded-lg transition"
              >
                Open Official ISRO PDF Report
              </button>
            </div>
          )}
        </div>

        {/* Right: Satellite Screen */}
        <div className="bg-space-800 border border-space-700 rounded-xl p-4 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-slate-400 uppercase">Satellite Sensor Output</span>
            <span className="text-[11px] font-mono text-cyan-400">
              {response ? `Latency: ${response.execution_trace.total_execution_time_ms} ms` : 'Standby'}
            </span>
          </div>

          <div className="relative w-full h-80 bg-black rounded-lg border border-space-700 overflow-hidden flex items-center justify-center">
            <img
              src={
                response?.result?.visual_evidence?.overlay_base64 ||
                activeDemo.image
              }
              alt="Live Satellite Display"
              className="w-full h-full object-contain"
            />
          </div>

          {response && (
            <div className="bg-space-900 p-3 rounded-lg border border-space-700 font-mono text-[11px] space-y-1">
              <div><b className="text-slate-400">Tool:</b> <span className="text-cyan-400">{response.execution_trace.tools_executed[0]?.tool_name}</span></div>
              <div><b className="text-slate-400">Model:</b> <span className="text-slate-300">{response.execution_trace.tools_executed[0]?.model_checkpoint}</span></div>
              <div><b className="text-slate-400">Trace ID:</b> <span className="text-slate-500">{response.execution_trace.trace_id}</span></div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
