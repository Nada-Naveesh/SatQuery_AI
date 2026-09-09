from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    label: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int
    score: float

class ImageMetadata(BaseModel):
    filename: str
    width: int
    height: int
    channels: int
    format: str
    modality: str  # optical, sar, multispectral, unknown
    crs: Optional[str] = "EPSG:4326"
    gsd_meters: Optional[float] = 10.0

class InputSummary(BaseModel):
    image_count: int
    modalities: List[str]
    dimensions: List[int]
    crs: Optional[str] = "EPSG:4326"
    resolution_m: Optional[float] = 10.0
    sensor: Optional[str] = None
    area: Optional[str] = None
    acquisition_date: Optional[str] = None
    data_source: Optional[str] = None

class VisualEvidence(BaseModel):
    evidence_type: str  # 'bounding_boxes', 'segmentation_mask', 'change_heatmap', 'fused_overlay'
    overlay_url: Optional[str] = None
    overlay_base64: Optional[str] = None
    bounding_boxes: Optional[List[BoundingBox]] = None
    metric_summary: Optional[Dict[str, Any]] = None

class ToolExecutionRecord(BaseModel):
    tool_name: str
    task_type: str
    model_checkpoint: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float
    confidence: float

class ExecutionTrace(BaseModel):
    trace_id: str
    timestamp: str
    detected_task: str
    router_reasoning: str
    input_configuration: str
    tools_executed: List[ToolExecutionRecord]
    total_execution_time_ms: float
    data_source_label: Optional[str] = None

class AnalysisResult(BaseModel):
    text_answer: str
    confidence_score: float
    visual_evidence: Optional[VisualEvidence] = None
    summary_bullet_points: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    status: str = "success"
    query: str
    detected_task: str
    input_summary: InputSummary
    result: AnalysisResult
    execution_trace: ExecutionTrace
    report_download_url: Optional[str] = None

class DemoScenario(BaseModel):
    id: str
    title: str
    category: str
    description: str
    default_query: str
    image_paths: List[str]
    input_type: str  # 'single', 'bitemporal_pair', 'optical_sar_pair'
    sensor: Optional[str] = None
    date: Optional[str] = None
    area: Optional[str] = None
    resolution: Optional[str] = None
    crs: Optional[str] = "EPSG:4326"
    suggested_queries: Optional[List[str]] = None
    real_data_source: Optional[str] = None
