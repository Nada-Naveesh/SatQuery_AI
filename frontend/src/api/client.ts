import { AnalysisResponse, DemoScenario } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function fetchScenarios(): Promise<DemoScenario[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenarios`);
  if (!res.ok) throw new Error('Failed to load demo scenarios');
  return res.json();
}

export async function executeAnalysis(
  query: string,
  files?: File[],
  scenarioId?: string,
  taskHint: string = 'auto'
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('query', query);
  formData.append('task_hint', taskHint);

  if (scenarioId) {
    formData.append('scenario_id', scenarioId);
  } else if (files && files.length > 0) {
    files.forEach((f) => formData.append('files', f));
  } else {
    throw new Error('Either scenarioId or at least one image file is required');
  }

  const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errData.detail || 'Analysis request failed');
  }

  return res.json();
}

export function getPdfReportUrl(traceId: string): string {
  return `${API_BASE_URL}/api/v1/report/pdf?trace_id=${encodeURIComponent(traceId)}`;
}
