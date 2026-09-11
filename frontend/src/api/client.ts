import { AnalysisResponse, DemoScenario } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function fetchScenarios(): Promise<DemoScenario[]> {
  const res = await fetch(`${API_BASE_URL}/api/scenarios`);
  if (!res.ok) throw new Error('Failed to load demo scenarios');
  return res.json();
}

export async function fetchScenarioDetail(scenarioId: string): Promise<DemoScenario> {
  const res = await fetch(`${API_BASE_URL}/api/scenarios/${encodeURIComponent(scenarioId)}`);
  if (!res.ok) throw new Error(`Failed to load scenario ${scenarioId}`);
  return res.json();
}

export async function fetchCatalogScenes(params?: {
  aoi?: string;
  sensor?: string;
  date_from?: string;
  date_to?: string;
  max_cloud_cover?: number;
}): Promise<{ scenes: any[] }> {
  const query = new URLSearchParams();
  if (params?.aoi) query.append('aoi', params.aoi);
  if (params?.sensor) query.append('sensor', params.sensor);
  if (params?.date_from) query.append('date_from', params.date_from);
  if (params?.date_to) query.append('date_to', params.date_to);
  if (params?.max_cloud_cover !== undefined) query.append('max_cloud_cover', params.max_cloud_cover.toString());

  const res = await fetch(`${API_BASE_URL}/api/scenes?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to query scene catalog');
  return res.json();
}

export async function fetchSceneDetail(sceneId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/scenes/${encodeURIComponent(sceneId)}`);
  if (!res.ok) throw new Error(`Failed to load scene ${sceneId}`);
  return res.json();
}

export async function executeAnalysis(
  query: string,
  files?: File[],
  scenarioId?: string,
  taskHint: string = 'auto',
  sceneIds?: string,
  analysisMode?: string
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('query', query);
  formData.append('task_hint', taskHint);

  if (sceneIds) {
    formData.append('scene_ids', sceneIds);
  }
  if (analysisMode) {
    formData.append('analysis_mode', analysisMode);
  }
  if (scenarioId) {
    formData.append('scenario_id', scenarioId);
  } else if (files && files.length > 0) {
    files.forEach((f) => formData.append('files', f));
  } else if (!sceneIds) {
    throw new Error('Either scenarioId, sceneIds, or at least one image file is required');
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

