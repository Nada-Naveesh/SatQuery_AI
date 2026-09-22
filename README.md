# SatQuery AI: Autonomous Geospatial Vision-Language Intelligence Platform

[![SIH 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://sih.gov.in)
[![Problem Statement](https://img.shields.io/badge/PS%20ID-26167-blue.svg)](https://sih.gov.in)
[![Organization](https://img.shields.io/badge/Organization-ISRO%20%2F%20SAC-success.svg)](https://www.isro.gov.in)
[![Theme](https://img.shields.io/badge/Theme-Space%20Technology-purple.svg)]()
[![Team](https://img.shields.io/badge/Team-Code%20Cosmos-crimson.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)]()

> **"A dominance-grade, autonomous vision-language operations assistant transforming multi-sensor satellite imagery (Sentinel-2, Cartosat, Sentinel-1 SAR) into evidence-grounded, natural-language insights with cryptographically auditable decision traces — engineered for ISRO, SAC, disaster response commanders, and urban planners."**

📘 **Quick Links:** [Live Place Analysis](docs/live_location_analysis.md) | [Upload Workflow](docs/upload_workflow.md) | [Area Calculation Engine](docs/area_calculation.md) | [Copernicus CDSE Integration](docs/copernicus_integration.md) | [System Architecture](docs/architecture.md) | [SIH 2026 Alignment Matrix](docs/sih_alignment.md) | [Operator Manual & Judge Demo](docs/OPERATOR_MANUAL.md)

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
   - Deep obsidian black (`#07080b`) and primary crimson (`#ef2b32`) operations command dashboard.
   - Fixed CSS `clip-path` split-comparison slider eliminating image distortion or aspect-ratio compression.
2. **Copernicus Data Space Ecosystem (CDSE) Ingestion**:
   - Automated dynamic discovery of Sentinel-2 L2A BOA reflectance tiles via `GET /api/copernicus/scenes`.
   - Geocodes arbitrary places in Andhra Pradesh, India, or worldwide with OpenStreetMap Nominatim.
3. **Certified Physical Area Statistics Engine (0.0 ha Prevention)**:
   - Derives real ground-truth surface areas in hectares using raster affine transform matrices and geodesic ellipsoidal math.
   - Displays real computed hectares only after analysis execution; honestly flags non-georeferenced imagery without false defaults.
4. **Asynchronous Remote Sensing Pipeline with Live Telemetry**:
   - Multi-stage background execution (`validating_scenes` $\to$ `retrieving_bands` $\to$ `aligning_images` $\to$ `masking_clouds` $\to$ `calculating_indices` $\to$ `detecting_changes` $\to$ `calculating_areas` $\to$ `rendering_overlay`).
5. **Calibrated Confidence Engine**:
   - Dynamic quality formula ($0.25 Q_{\text{valid}} + 0.20 Q_{\text{cloud}} + 0.20 Q_{\text{overlap}} + 0.20 Q_{\text{reg}} + 0.15 Q_{\text{signal}}$).
6. **Explainable Semantic Multi-Color Overlays**:
   - High-contrast 5-class delineation with on-map legend revealed only upon overlay generation:
     - 🔴 **Red (`#ef4444`)**: New built-up & impervious surfaces.
     - 🟢 **Green (`#22c55e`)**: Crop emergence & vegetation canopy increase.
     - 🟡 **Yellow (`#eab308`)**: Vegetation clearing & disturbance.
     - 🔵 **Cyan (`#06b6d4`)**: Water surface expansion & flood inundation.
     - 🟣 **Purple (`#a855f7`)**: Water recession & dry-up.
7. **One-Click Official Mission PDF Report**:
   - Generates multi-page intelligence briefings via ReportLab with 3-image visual comparison tables, executive summaries, and tamper-evident audit IDs.

---

## 3. System Architecture

```
+---------------------------------------------------------------------------------------+
|                    Dominance-Grade Mission Control Dashboard                          |
|  - Black Obsidian (#07080b) & Crimson Red (#ef2b32) Defense Intelligence UI          |
|  - 2 Workflows: Explore a Live Location (Nominatim + CDSE) | Upload Imagery Pair      |
|  - Fixed CSS Clip-Path Split Slider, Evidence Overlay with Opacity, Side-by-Side      |
|  - Real physical hectare stats card revealed only upon analysis completion            |
|  - Asynchronous pipeline telemetry modal with real-time stage progress updates        |
|  - Official Mission PDF Report Generator                                              |
+------------------------------------------+--------------------------------------------+
                                           | HTTP / REST (Multipart / Form-Data / JSON)
                                           v
+---------------------------------------------------------------------------------------+
|                              FastAPI Gateway Server                                   |
|  - Route: GET  /                          (Self-contained Mission Control UI)         |
|  - Route: GET  /api/location/search       (Nominatim geocoding & spatial bounding box)|
|  - Route: GET  /api/copernicus/scenes     (Live Copernicus CDSE discovery + fallback) |
|  - Route: POST /api/analysis/start        (Asynchronous pipeline job initiator)       |
|  - Route: GET  /api/analysis/{job_id}     (Real-time pipeline stage telemetry)        |
|  - Route: GET  /api/analysis/{job}/results(Physical area breakdown in hectares)       |
|  - Route: GET  /api/analysis/{job}/overlay(Classified 4-channel transparent PNG)      |
|  - Route: GET  /api/analysis/{job}/report (Official PDF Mission Report Generator)     |
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
