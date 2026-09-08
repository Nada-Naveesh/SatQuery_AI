export interface BoundingBox {
  label: string;
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
  score: number;
}

export interface InputSummary {
  image_count: number;
  modalities: string[];
  dimensions: number[];
  crs?: string;
  resolution_m?: number;
}

export interface VisualEvidence {
  evidence_type: 'bounding_boxes' | 'segmentation_mask' | 'change_heatmap' | 'fused_overlay';
  overlay_url?: string;
  overlay_base64?: string;
  bounding_boxes?: BoundingBox[];
  metric_summary?: Record<string, any>;
}

export interface ToolExecutionRecord {
  tool_name: string;
  task_type: string;
  model_checkpoint: string;
  parameters: Record<string, any>;
  execution_time_ms: number;
  confidence: number;
}

export interface ExecutionTrace {
  trace_id: string;
  timestamp: string;
  detected_task: string;
  router_reasoning: string;
  input_configuration: string;
  tools_executed: ToolExecutionRecord[];
  total_execution_time_ms: number;
}

export interface AnalysisResult {
  text_answer: string;
  confidence_score: number;
  visual_evidence?: VisualEvidence;
  summary_bullet_points?: string[];
}

export interface AnalysisResponse {
  status: string;
  query: string;
  detected_task: string;
  input_summary: InputSummary;
  result: AnalysisResult;
  execution_trace: ExecutionTrace;
  report_download_url?: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  category: string;
  description: string;
  default_query: string;
  image_paths: string[];
  input_type: 'single' | 'bitemporal_pair' | 'optical_sar_pair';
}
