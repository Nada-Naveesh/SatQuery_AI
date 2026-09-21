# SatQuery AI: Autonomous Geospatial Vision-Language Intelligence Platform

[![SIH 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://sih.gov.in)
[![Problem Statement](https://img.shields.io/badge/PS%20ID-26167-blue.svg)](https://sih.gov.in)
[![Organization](https://img.shields.io/badge/Organization-ISRO%20%2F%20SAC-success.svg)](https://www.isro.gov.in)
[![Theme](https://img.shields.io/badge/Theme-Space%20Technology-purple.svg)]()
[![Team](https://img.shields.io/badge/Team-Code%20Cosmos-crimson.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)]()

> **"A dominance-grade, autonomous vision-language operations assistant transforming multi-sensor satellite imagery (Sentinel-2, Cartosat, Sentinel-1 SAR) into evidence-grounded, natural-language insights with cryptographically auditable decision traces — engineered for ISRO, SAC, disaster response commanders, and urban planners."**

📘 **Quick Links:** [Copernicus CDSE Integration](docs/copernicus_integration.md) | [System Architecture](docs/architecture.md) | [SIH 2026 Alignment Matrix](docs/sih_alignment.md) | [Operator Manual & Judge Demo](docs/OPERATOR_MANUAL.md) | [Where to Get Free Satellite Data](docs/how_to_get_data.md) | [Benchmark Results](docs/benchmark_results.md)

---

## 1. Quickstart — Zero Setup 1-Click Launch

SatQuery AI ships with an integrated, zero-setup **Mission Control Single-Page Application** served directly from the FastAPI engine:

```bash
# 1. Clone the repository
git clone https://github.com/Nada-Naveesh/SatQuery_AI.git
cd SatQuery_AI

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Launch the Mission Control Server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

*(No Node.js or npm compilation required to experience the full dominance-grade interface!)*

---

## 2. Key Dominance-Grade Capabilities (SIH 2026 PS 26167)

1. **Defense-Grade Black & Red UI Theme**:
   - Deep void black (`#070709`) and crimson red (`#ef4444`) operations dashboard.
   - Interactive split-slider comparison, opacity blending, and real-time zoom.
2. **Copernicus Data Space Ecosystem (CDSE) Ingestion**:
   - Automated dynamic discovery of Sentinel-2 L2A BOA reflectance tiles via `GET /api/copernicus/scenes`.
   - Geocodes arbitrary places in Andhra Pradesh, India, or worldwide with deterministic offline catalog fallback.
3. **Calibrated Confidence Engine**:
   - Every response provides both a normalized numerical score ($\ge 0.85$) and plain English reasoning (`result.confidence_explanation`) detailing spectral quality, sensor ground resolution, and model alignment.
4. **Explainable Semantic Multi-Color Overlays**:
   - High-contrast 4-color change delineation with interactive on-map legend:
     - 🔴 **Red (`#ef4444`)**: Built-up infrastructure & new constructions.
     - 🟢 **Green (`#22c55e`)**: Crop emergence, agriculture & vegetation.
     - 🔵 **Blue (`#3b82f6`)**: Water body expansion & flood inundation.
     - 🟡 **Amber (`#f59e0b`)**: General surface spectral variance.
5. **Multi-Query Conversational Sessions**:
   - Session tracking via `session_trace_id` enables subsequent questions on the active scene without re-uploading raster tensors.
6. **Auditable Cryptographic Traces**:
   - Every tool execution produces a SHA-256 hashed trace accessible via `GET /api/traces/{trace_id}`.
7. **One-Click Official Mission PDF Report**:
   - Generates multi-page intelligence briefings via ReportLab with 3-image visual comparison tables, executive summaries, and tamper-evident audit IDs.

---

## 3. Preloaded Demonstration Scenarios

SatQuery AI includes 3 preloaded 1-click scenarios designed for instant evaluation:

| Scenario | Location & Sensor | Suggested Query | Key Output |
| :--- | :--- | :--- | :--- |
| **1. Urban Infrastructure Sprawl** | Gudlavalleru & Vijayawada (Sentinel-2 L2A, 10m GSD, 2025 vs 2026) | *"What infrastructure changes occurred between 2025 and 2026?"* | Delineates built-up expansion in red, agricultural clearance in green, with hectare calculations. |
| **2. Coastal Port & Breakwater Extension** | Visakhapatnam Deepwater Port (Sentinel-2 L2A, 10m GSD, 2025 vs 2026) | *"Inspect coastal construction and breakwater infrastructure development."* | Identifies maritime marine breakwater extensions and paved cargo storage zones. |
| **3. Flood Inundation & Agrarian Recovery** | Godavari River Basin, AP (Sentinel-2 L2A + Sentinel-1 SAR) | *"Identify waterlogged agricultural parcels and flood extents."* | Multi-spectral water index ($\text{NDWI} \ge 0.15$) and SAR dielectric attenuation ($\le -21\text{ dB}$). |

---

## 4. System Architecture

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

## 5. Working Manual — How to Use SatQuery AI

### Mode 1: 1-Click Instant Scenarios
1. Open [http://localhost:8000](http://localhost:8000).
2. Click any of the preloaded scenarios in the left panel (**Gudlavalleru**, **Visakhapatnam**, or **Godavari Basin**).
3. The sample satellite imagery and pre-configured analytical query will load automatically.
4. Click **Run Analysis**.
5. Inspect the generated answer, confidence score, plain English calibration rationale, and interactive overlay.
6. Drag the horizontal split comparison slider to inspect 2025 vs 2026 change dynamics.
7. Click **Download PDF Report** to export the verified briefing.

### Mode 2: Live Copernicus Discovery
1. Switch to the **Copernicus Discovery** tab in Mission Control.
2. Enter any location name (e.g., `Amaravati`, `Vijayawada`, `Kakinada`, `Tirupati`).
3. Click **Search CDSE**.
4. The system queries Copernicus Data Space Ecosystem and displays matching Sentinel-2 L2A tiles.
5. Select a candidate scene and click **Run Analysis on Scene**.

### Mode 3: Uploading Custom Satellite GeoTIFFs
1. Switch to the **Custom Upload** tab.
2. Drag and drop your `.tif` or `.png` satellite scenes (upload 1 for single-image VQA/grounding, or 2 for bi-temporal change detection).
3. Enter your question in plain English (e.g., *"What changed here between the two dates?"*).
4. Click **Run Analysis**.

### Mode 4: Asking Multi-Query Follow-ups
1. After running any analysis, scroll down to the **Multi-Query Dialogue Thread**.
2. Type a follow-up question (e.g., *"Summarize the infrastructure expansion in hectares"* or *"What is the flood impact on nearby transportation links?"*).
3. Click **Ask Follow-up**. SatQuery AI uses the cached `session_trace_id` to answer instantly without re-uploading files.

---

## 6. Testing & Quality Assurance

The codebase includes an exhaustive test suite covering all endpoints, agent tools, physics heuristics, and Copernicus integrations:

```bash
# Run the entire test suite
python -m pytest tests/ -v
```

**Results:** 46/46 passed (100% test pass rate).

---

## 7. License & Credits

Developed by **Team Code Cosmos** for **Smart India Hackathon 2026** (Problem Statement ID: **26167**).  
Licensed under the Apache License, Version 2.0.
