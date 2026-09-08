# SatQuery AI - System Architecture Specification (PS 26167)

## 1. End-to-End System Data Flow

```
+-----------------------------------------------------------------------------------+
|                              Frontend Web Application                             |
|  - Multi-panel viewport (Base image, Overlays, Side-by-side, Optical vs SAR)      |
|  - Dynamic query bar with auto-suggestions & task hints                           |
|  - Real-time execution trace visualization (DAG telemetry)                        |
|  - Downloadable Intelligence Reports (PDF & GeoJSON)                              |
+-----------------------------------------+-----------------------------------------+
                                          | Multipart Form Data (Images + Query)
                                          v
+-----------------------------------------------------------------------------------+
|                              FastAPI Gateway Server                               |
|  - Route: /api/v1/analyze                                                         |
|  - Route: /api/v1/health                                                          |
|  - Route: /api/v1/report/pdf                                                      |
+-----------------------------------------+-----------------------------------------+
                                          | Parsed Request + Temp In-Memory Buffers
                                          v
+-----------------------------------------------------------------------------------+
|                         Geospatial & Input Validator                              |
|  - Image format verification (GeoTIFF, TIFF, PNG, JPEG)                           |
|  - Metadata extraction (CRS, spatial extent, ground sampling distance, bands)    |
|  - Pair compatibility check (temporal alignment, cross-modal optical-SAR tags)   |
+-----------------------------------------+-----------------------------------------+
                                          | Validated Images + Query
                                          v
+-----------------------------------------------------------------------------------+
|                       Agentic Orchestration Controller                            |
|  - Rule-based Intent Classifier (Keyword + Syntax + Modality heuristic)           |
|  - Dynamic Task Graph (DAG) construction                                          |
|  - Tool Dispatcher & Execution Sandbox                                            |
|  - Execution Trace Telemetry Logger (Timestamps, params, confidence, subtasks)   |
+-----------------------------------------+-----------------------------------------+
                                          |
         +--------------------------------+--------------------------------+
         |                                |                                |
         v                                v                                v
+----------------------+        +----------------------+        +----------------------+
| Single-Image VQA     |        | Bi-Temporal Change   |        | Optical-SAR Fusion   |
| - Text-guided visual |        | - Siamese feature    |        | - Joint cross-modal  |
|   question answering |        |   differencing       |        |   feature extraction |
| - Referring express. |        | - Change mask        |        | - Penetration        |
|   region grounding   |        | - Categorical summary|        |   land-cover mapping |
+----------+-----------+        +----------+-----------+        +----------+-----------+
         |                                |                                |
         +--------------------------------+--------------------------------+
                                          | Aggregated ToolResult
                                          v
+-----------------------------------------------------------------------------------+
|                         Evidence & Response Aggregator                            |
|  - Confidence Score Normalization                                                 |
|  - Visual Evidence Serialization (Heatmaps, Bounding Boxes, Segmentation Masks)   |
|  - Structured Trace Generation (JSON payload)                                     |
|  - PDF Mission Intelligence Exporter (ReportLab)                                  |
+-----------------------------------------------------------------------------------+
```

## 2. Component Specifications

### 2.1 Geospatial Input Validator (`validators.py`)
- Detects whether input is single-image, bi-temporal pair, or co-registered Optical-SAR pair.
- Normalizes multiband imagery (e.g. Sentinel-2 12-band to RGB/False-color, Sentinel-1 VV/VH to decibel scale).
- Confirms spatial bounding overlaps for temporal pairs.

### 2.2 Agentic Controller (`controller.py`)
- Employs deterministic intent classification to map queries to specialist tools:
  - `visual_question_answering`: `"what is"`, `"how many"`, `"is there"`, `"classify"`.
  - `region_grounding`: `"locate"`, `"highlight"`, `"where is"`, `"find the polygon"`.
  - `change_analysis`: `"what changed"`, `"compare dates"`, `"infrastructure growth"`, `"difference"`.
  - `optical_sar_fusion`: queries targeting all-weather, cloud penetration, flood/water segmentation with SAR cues.
- Emits an auditable telemetry log:
  ```json
  {
    "query": "Highlight all water reservoirs and calculate confidence",
    "detected_task": "region_grounding",
    "input_mode": "single_optical",
    "selected_tool": "GroundingTool_v1",
    "parameters": {"threshold": 0.5, "box_expansion": 0.05},
    "execution_time_ms": 142.5,
    "confidence": 0.942
  }
  ```

### 2.3 Specialist Tool Registry (`registry.py`)
Standardized tool execution contract:
```python
class BaseTool(ABC):
    @abstractmethod
    def run(self, images: List[np.ndarray], query: Optional[str], params: Dict) -> ToolResult:
        pass
```
