import React, { useState } from 'react';
import Head from 'next/head';
import { UploadPanel } from '../components/UploadPanel';
import { QueryPanel } from '../components/QueryPanel';
import { ImageViewer } from '../components/ImageViewer';
import { ResultCard } from '../components/ResultCard';
import { ExecutionTrace } from '../components/ExecutionTrace';
import { ReportDownload } from '../components/ReportDownload';
import { executeAnalysis } from '../api/client';
import { AnalysisResponse } from '../types';

export default function Dashboard() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>('scenario_1_flood');
  const [query, setQuery] = useState(
    'Identify the submerged agricultural parcels and highlight their spatial boundaries.'
  );
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AnalysisResponse | null>(null);

  const baseImagePreview =
    selectedFiles.length > 0
      ? URL.createObjectURL(selectedFiles[0])
      : activeScenarioId === 'scenario_today_near_real_time'
      ? '/static/latest/latest_scene.png'
      : activeScenarioId === 'scenario_4_coastal'
      ? '/static/demo_scenarios/scenario_4_coastal/t2.png'
      : activeScenarioId === 'scenario_2_urban'
      ? '/static/demo_scenarios/scenario_2_urban/t2.png'
      : activeScenarioId === 'scenario_3_optical_sar'
      ? '/static/demo_scenarios/scenario_3_optical_sar/optical.png'
      : '/static/demo_scenarios/scenario_1_flood/image1.png';

  const handleSelectScenario = (id: string, q: string) => {
    setActiveScenarioId(id);
    setSelectedFiles([]);
    setQuery(q);
  };

  const handleRun = async () => {
    setIsLoading(true);
    try {
      const res = await executeAnalysis(
        query,
        selectedFiles.length > 0 ? selectedFiles : undefined,
        activeScenarioId || undefined
      );
      setResponse(res);
    } catch (err: any) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-space-900 text-slate-100 min-h-screen flex flex-col font-sans">
      <Head>
        <title>SatQuery AI — ISRO Remote Sensing Vision-Language Assistant</title>
      </Head>

      <header className="border-b border-space-700 bg-space-800/80 backdrop-blur sticky top-0 z-50 h-16 flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <span className="font-bold text-lg bg-gradient-to-r from-white via-cyan-200 to-blue-400 bg-clip-text text-transparent">
            SatQuery AI
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
            PS 26167
          </span>
        </div>
        <ReportDownload traceId={response?.execution_trace?.trace_id} />
      </header>

      <div className="bg-gradient-to-r from-cyan-950/80 via-blue-950/80 to-slate-900 border-b border-cyan-800/40 px-6 py-2 flex items-center justify-between text-xs text-slate-300">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-semibold text-white">Real Satellite Imagery Active:</span>
          <span className="text-slate-400 hidden sm:inline">Preloaded GeoTIFF chips (Sentinel-2 L2A, Cartosat-2S, Sentinel-1 SAR, LEVIR-CD)</span>
        </div>
        <span className="font-mono text-[11px] text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">ISRO / SAC Ready</span>
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 space-y-4">
          <div className="border border-space-700 bg-space-800 rounded-xl p-4 space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              ISRO Demonstration Scenarios
            </h3>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_today_near_real_time',
                  'Detect recent surface changes, water inundation, and newly emerged infrastructure.'
                )
              }
              className={`w-full text-left p-2.5 rounded border transition text-xs ${
                activeScenarioId === 'scenario_today_near_real_time'
                  ? 'border-emerald-500 bg-emerald-950/40'
                  : 'border-emerald-900/60 bg-emerald-950/20 hover:border-emerald-500/60'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="font-semibold text-emerald-300 flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Today's Live Surveillance Stream</span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-900/60 text-emerald-300">Near-Real-Time</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Sentinel-2 L2A &bull; Acquired & Ingested Today (10m GSD)</div>
            </button>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_1_flood',
                  'Identify the submerged agricultural parcels and highlight their spatial boundaries.'
                )
              }
              className={`w-full text-left p-2.5 rounded border transition text-xs ${
                activeScenarioId === 'scenario_1_flood'
                  ? 'border-cyan-500 bg-space-900'
                  : 'border-space-700 bg-space-900/60 hover:border-cyan-500/60'
              }`}
            >
              <div className="font-semibold text-white">1. Flood Inundation (Single Optical)</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Sentinel-2 L2A MSI &bull; Godavari Basin, AP (10m GSD)</div>
            </button>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_2_urban',
                  'What major infrastructure changes occurred between these two acquisition dates?'
                )
              }
              className={`w-full text-left p-2.5 rounded border transition text-xs ${
                activeScenarioId === 'scenario_2_urban'
                  ? 'border-cyan-500 bg-space-900'
                  : 'border-space-700 bg-space-900/60 hover:border-cyan-500/60'
              }`}
            >
              <div className="font-semibold text-white">2. Urban Infrastructure Sprawl (Bi-temporal Pair)</div>
              <div className="text-[11px] text-slate-400 mt-0.5">LEVIR-CD Bi-temporal Satellites (2022 vs 2024 &bull; 0.5m GSD)</div>
            </button>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_3_optical_sar',
                  'Penetrate cloud cover to map industrial storage tanks and coastal water bodies.'
                )
              }
              className={`w-full text-left p-2.5 rounded border transition text-xs ${
                activeScenarioId === 'scenario_3_optical_sar'
                  ? 'border-cyan-500 bg-space-900'
                  : 'border-space-700 bg-space-900/60 hover:border-cyan-500/60'
              }`}
            >
              <div className="font-semibold text-white">3. Optical-SAR Cloud Penetration</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Cartosat-2S (0.65m) + Sentinel-1 C-SAR (82% Cloud Cover)</div>
            </button>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_4_coastal',
                  'What new coastal infrastructure or breakwater structures were constructed between T1 and T2?'
                )
              }
              className={`w-full text-left p-2.5 rounded border transition text-xs ${
                activeScenarioId === 'scenario_4_coastal'
                  ? 'border-cyan-500 bg-space-900'
                  : 'border-space-700 bg-space-900/60 hover:border-cyan-500/60'
              }`}
            >
              <div className="font-semibold text-white">4. Coastal Port & Breakwater Expansion</div>
              <div className="text-[11px] text-slate-400 mt-0.5">Visakhapatnam Port 2023 vs 2024 (Sentinel-2 &bull; 10m GSD)</div>
            </button>
          </div>

          <QueryPanel
            query={query}
            setQuery={setQuery}
            onExecute={handleRun}
            isLoading={isLoading}
          />

          <UploadPanel
            onFilesSelected={(files) => {
              setSelectedFiles(files);
              setActiveScenarioId(null);
            }}
            selectedFiles={selectedFiles}
            activeScenarioId={activeScenarioId}
          />
        </div>

        <div className="lg:col-span-7 space-y-4">
          <ImageViewer
            baseImageUrl={baseImagePreview}
            visualEvidence={response?.result?.visual_evidence}
            detectedTask={response?.detected_task}
            dimensions={response?.input_summary?.dimensions}
            resolutionM={response?.input_summary?.resolution_m}
            sensor={response?.input_summary?.sensor}
            dataSource={response?.input_summary?.real_data_source}
            crs={response?.input_summary?.crs}
          />
          <ResultCard result={response?.result} />
          <ExecutionTrace trace={response?.execution_trace} />
        </div>
      </main>
    </div>
  );
}
