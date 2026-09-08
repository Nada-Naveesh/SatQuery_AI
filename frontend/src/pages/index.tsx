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
      : activeScenarioId === 'scenario_2_urban'
      ? '/static/samples/urban_t2_2024.png'
      : activeScenarioId === 'scenario_3_optical_sar'
      ? '/static/samples/co_registered_optical_cloudy.png'
      : '/static/samples/flood_sentinel2_optical.png';

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

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 space-y-4">
          <div className="border border-space-700 bg-space-800 rounded-xl p-4 space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              ISRO Demonstration Scenarios
            </h3>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_1_flood',
                  'Identify the submerged agricultural parcels and highlight their spatial boundaries.'
                )
              }
              className="w-full text-left p-2.5 rounded border border-space-700 bg-space-900/60 hover:border-cyan-500 text-xs"
            >
              1. Flood Inundation (Single Optical)
            </button>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_2_urban',
                  'What major infrastructure changes occurred between these two acquisition dates?'
                )
              }
              className="w-full text-left p-2.5 rounded border border-space-700 bg-space-900/60 hover:border-cyan-500 text-xs"
            >
              2. Urban Infrastructure Sprawl (Bi-temporal Pair)
            </button>
            <button
              onClick={() =>
                handleSelectScenario(
                  'scenario_3_optical_sar',
                  'Penetrate cloud cover to map industrial storage tanks and coastal water bodies.'
                )
              }
              className="w-full text-left p-2.5 rounded border border-space-700 bg-space-900/60 hover:border-cyan-500 text-xs"
            >
              3. Optical-SAR Cloud Penetration (Cartosat + RISAT)
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
          />
          <ResultCard result={response?.result} />
          <ExecutionTrace trace={response?.execution_trace} />
        </div>
      </main>
    </div>
  );
}
