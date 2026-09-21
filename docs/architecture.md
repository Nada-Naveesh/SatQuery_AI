# SatQuery AI — System Architecture Specification (SIH 2026 PS 26167)

**Interactive Vision-Language Assistant for Multimodal Remote Sensing Analysis**  
**Theme:** Space Technology | **Category:** Software | **Organization:** Indian Space Research Organisation (ISRO) / SAC

---

## 1. End-to-End System Architecture

```
+---------------------------------------------------------------------------------------+
|                    Dominance-Grade Mission Control Dashboard                          |
|  - Black Void (#070709) & Crimson Red (#ef4444) Defense Intelligence UI              |
|  - 3 Operating Modes: 1-Click Scenarios | Copernicus CDSE Discovery | Custom Upload    |
|  - Multi-panel viewer: RGB Base, Comparison, Explainable Semantic Overlay, Swipe      |
|  - On-map interactive legend (Red: Built-up, Green: Vegetation, Blue: Water)          |
|  - Multi-query session thread with session_trace_id persistence                       |
|  - Auditable cryptographic DAG execution trace modal + PDF Report Download            |
+------------------------------------------+--------------------------------------------+
                                           | HTTP / REST (Multipart / Form-Data / JSON)
                                           v
+---------------------------------------------------------------------------------------+
|                              FastAPI Gateway Server                                   |
|  - Route: GET  /                       (Zero-setup self-contained Mission Control UI) |
|  - Route: POST /api/v1/analyze         (Agentic query endpoint + multi-query caching) |
|  - Route: GET  /api/copernicus/scenes  (Live Copernicus CDSE discovery + fallback)    |
|  - Route: GET  /api/traces/{trace_id}  (Auditable execution traces)                   |
|  - Route: GET  /api/v1/report/pdf      (Official PDF Mission Report Generator)        |
+------------------------------------------+--------------------------------------------+
                                           | Parsed In-Memory Arrays & Georeferencing
                                           v
+---------------------------------------------------------------------------------------+
|                    Geospatial Validator & Session Cache Manager                       |
|  - Formats: Multi-band GeoTIFF, TIFF, PNG, JPEG                                       |
|  - Modality heuristics: Optical Multispectral, SAR VV/VH, Co-registered pairs         |
|  - Multi-query session caching: Recycles imagery by session_trace_id without reload   |
|  - Andhra Pradesh State-Wide Catalog: 11 urban & rural AOIs (2025 vs 2026)            |
+------------------------------------------+--------------------------------------------+
                                           | Validated Satellite Arrays + Query
                                           v
+---------------------------------------------------------------------------------------+
|                        Agentic Controller & Task Orchestrator                         |
|  - Heuristic & Semantic Intent Router (VQA, Grounding, Change Detection, SAR Fusion)  |
|  - Execution Trace Telemetry (Sha256 integrity hash, latencies, params, subtasks)     |
|  - Calibrated Confidence Engine: Math score + Plain English reasoning explanation     |
+------------------------------------------+--------------------------------------------+
                                           |
         +---------------------------------+---------------------------------+
         |                                 |                                 |
         v                                 v                                 v
+-----------------------+       +-----------------------+       +-----------------------+
| Single-Image VQA      |       | Bi-Temporal Change    |       | Optical-SAR Fusion    |
| - Text-guided visual  |       | - Multi-spectral diff |       | - Cross-modal feature |
|   question answering  |       | - Semantic 4-color    |       |   fusion (S1 + S2)    |
| - Region grounding    |       |   explainable overlay |       | - Cloud penetration   |
|   & bounding boxes    |       |   (Red/Green/Blue)    |       | - Flood mapping       |
+-----------+-----------+       +-----------+-----------+       +-----------+-----------+
         |                                 |                                 |
         +---------------------------------+---------------------------------+
                                           | ToolResult (Array + Overlay + Metrics)
                                           v
+---------------------------------------------------------------------------------------+
|                           Evidence & Report Aggregator                                |
|  - High-resolution RGBA semantic overlay generation                                  |
|  - Calibrated confidence explanation synthesis                                        |
|  - Cryptographic execution trace storage in SESSION_TRACES                            |
|  - Multi-page Intelligence Briefing PDF generation (ReportLab)                        |
+---------------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 Agentic Multi-Tool Orchestrator (`backend/app/agent/controller.py`)
- Automatically dispatches complex natural language queries to specialized remote-sensing analytical tools.
- Generates transparent, auditable DAG traces returned via `GET /api/traces/{trace_id}`.
- Calibrates confidence scores and produces operator-friendly `confidence_explanation` strings explaining why confidence is high, moderate, or conditional.

### 2.2 Explainable Semantic Multi-Color Overlays (`backend/app/tools/change_tool.py`)
- Generates pixel-accurate 4-color semantic masks:
  - **Red (`#ef4444`)**: Built-up infrastructure and newly constructed impermeable surfaces.
  - **Green (`#22c55e`)**: Crop emergence, afforestation, and vegetation expansion.
  - **Blue (`#3b82f6`)**: Water body expansion, reservoir replenishment, and flood inundation.
  - **Amber (`#f59e0b`)**: General surface spectral variance.
- Accompanied by interactive, on-map legend and metric breakdowns.

### 2.3 Copernicus Data Space Ecosystem (CDSE) Ingestion (`backend/app/services/copernicus_service.py`)
- Connects to ESA Copernicus OData and STAC APIs for automatic discovery of Sentinel-2 L2A BOA reflectance tiles.
- Built-in geocoder resolves any place name in Andhra Pradesh, India, or worldwide.
- Built-in local catalog fallback ensures 100% test pass rate and uninterrupted demonstration during hackathon judging.

### 2.4 Multi-Query Conversational Session Handling
- Operators can ask subsequent analytical questions regarding an existing scene using `session_trace_id`.
- Reuses in-memory raster tensors and preserves conversational context across multiple turns without needing file re-uploads.

---

## 3. Design System & UI Specifications

- **Palette**: Deep Void Black (`#070709`, `#0d0d12`), Crimson Red (`#ef4444`, `#dc2626`), Crisp White and Slate (`#f8fafc`, `#94a3b8`).
- **Typography**: Inter (modern sans-serif) + JetBrains Mono (cryptographic hashes, coordinates, metrics).
- **Interface**: Zero-setup, responsive Single Page Application delivered directly by FastAPI at `http://localhost:8000/`.
