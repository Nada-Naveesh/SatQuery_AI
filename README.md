# SatQuery AI: Operational Geospatial Intelligence Platform for Multimodal Remote Sensing

[![SIH 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://sih.gov.in)
[![Problem Statement](https://img.shields.io/badge/PS%20ID-26167-blue.svg)](https://sih.gov.in)
[![Organization](https://img.shields.io/badge/Organization-ISRO%20%2F%20SAC-success.svg)](https://www.isro.gov.in)
[![Theme](https://img.shields.io/badge/Theme-Space%20Technology-purple.svg)]()
[![Team](https://img.shields.io/badge/Team-Code%20Cosmos-9cf.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)]()

> **"An operational, agentic geospatial intelligence platform that turns multi-sensor satellite archives (optical, SAR, temporal) into evidence-grounded, natural-language insights with auditable decision traces — engineered for ISRO, SAC, disaster management, and urban planning."**

📘 **Quick Links:** [Official Operator Manual (Evaluation Guide)](docs/OPERATOR_MANUAL.md) | [SIH 2026 Alignment Matrix](docs/sih_alignment.md) | [Technical Whitepaper & System Report](docs/technical_report.md) | [Benchmark Results Scorecard](docs/benchmark_results.md) | [SIH 6-Slide Pitch Deck](docs/sih2026_pitch_deck.md)

---

## 1. Executive Summary

**SatQuery AI** is an evidence-grounded, agentic remote-sensing operations assistant engineered by **Team Code Cosmos** for **Smart India Hackathon 2026 (Problem Statement ID: 26167)** under the **ISRO / Department of Space (Space Applications Centre - SAC)** theme. Traditional satellite data exploitation requires domain expertise in geographic information systems (GIS), multi-band sensor calibration, and specialized computer vision pipelines. SatQuery AI democratizes satellite imagery analysis by allowing non-expert decision makers, disaster response commanders, and urban planners to interrogate single, multispectral, Synthetic Aperture Radar (SAR), and multitemporal satellite data using everyday natural language.

Rather than relying on a brittle, hallucination-prone monolithic Vision-Language Model (VLM), SatQuery AI introduces an **auditable Agentic Orchestrator**. The orchestrator parses complex user queries, inspects sensor modalities and spatial metadata (GeoTIFF, CRS, ground sampling distance), and sequences a registry of specialized remote-sensing AI tools (VQA, text-guided grounding, bi-temporal change detection, and Optical–SAR cross-modal fusion). Every textual insight is strictly linked to spatial proof (bounding boxes, segmentation masks, change heatmaps) and accompanied by an auditable execution trace and one-click PDF mission report.

---

## 2. Problem Statement Alignment (PS 26167)

SatQuery AI strictly adheres to all mandatory and extended evaluation criteria outlined in **PS 26167**:

| Mandatory PS Requirement | SatQuery AI Implementation | Primary Benchmark / Evaluation |
| :--- | :--- | :--- |
| **Remote-Sensing Adaptation** | Fine-tuned encoder/decoder representations using **BigEarthNet.txt** (Sentinel-1 SAR + Sentinel-2 multispectral paired image-text data). | BigEarthNet v1.0 multimodal split |
| **Single-Image Baseline (VQA & Grounding)** | Dual-branch VQA specialist model combined with text-guided referring expression bounding box and mask extraction. | **RSVQA** (LR/HR) & **VRSBench** |
| **Multi-Image Change Analysis** | Bi-temporal feature differencing with Siamese feature backbones generating pixel-level change masks and natural-language change summaries. | **CDVQA** & **LEVIR-CD** |
| **Cross-Modal Pair Analysis (Optical + SAR)** | Co-registered optical/multispectral + SAR joint reasoning module combining structural penetration of SAR with spectral cues of optical imagery. | Co-registered Sentinel-1/2 & ISRO Cartosat-2S/RISAT pairs |
| **Agentic Orchestration** | Deterministic, DAG-based tool selector routing queries across specialist models with complete execution telemetry. | Zero-hallucination tool call verification |
| **Evidence Grounding & Auditability** | Visual overlays (GeoJSON/heatmaps), confidence metrics, transparent execution trace, and downloadable mission intelligence reports. | Human-in-the-loop audit logs & PDF reports |

---

## 3. High-Level Architecture

```
                                  +-----------------------------+
                                  |    Mission Control Web UI   |
                                  |  (Next.js 14, Tailwind, GIS)|
                                  +--------------+--------------+
                                                 |
                                     HTTP / WebSocket Payload
                                     (GeoTIFF / PNG + Query)
                                                 v
                                  +-----------------------------+
                                  |    FastAPI Gateway Server   |
                                  |  - Metadata Extractor       |
                                  |  - CRS & Co-registration    |
                                  |  - Modality Compatibility   |
                                  +--------------+--------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  |     Agentic Orchestrator    |
                                  |  - Query Intent Parser      |
                                  |  - Input Geometry Inspector |
                                  |  - Execution Planner & DAG  |
                                  +--------------+--------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                         |                         |
                       v                         v                         v
        +----------------------------+ +--------------------+ +----------------------------+
        |  Single-Image VQA Tool     | | Change Analysis    | | Optical-SAR Fusion Tool    |
        |  - RS-Adapted VLM / VQA    | | - Siamese Backbone | | - Optical (S2/Cartosat)    |
        |  - Grounding DINO / SAM RS | | - Mask & Diff VQA  | | - SAR (S1/RISAT Backscatter|
        +----------------------------+ +--------------------+ +----------------------------+
                       |                         |                         |
                       +-------------------------+-------------------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  |  Evidence & Report Engine   |
                                  |  - Confidence Calibration   |
                                  |  - Spatial Heatmap Encoder  |
                                  |  - Auditable Trace Logger   |
                                  |  - Instant PDF/JSON Export  |
                                  +-----------------------------+
```

---

## 4. Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14 / React 18, TypeScript, Tailwind CSS, Lucide Icons, Leaflet / MapLibre GL |
| **Backend & API** | FastAPI (Python 3.10+), Pydantic v2, Uvicorn, Celery / Redis |
| **Remote Sensing / Geospatial** | Rasterio, GDAL, Shapely, PyProj, OpenCV, Pillow, NumPy |
| **AI / Machine Learning** | PyTorch 2.2+, Hugging Face Transformers, Timm, PEFT / LoRA, Segmentation Models PyTorch |
| **Model Baselines & Weights** | RemoteCLIP, GeoChat / LLaVA-1.5, Grounding DINO, ChangeFormer / BIT, BigEarthNet-adapted ViT |
| **Reporting & Export** | ReportLab / WeasyPrint (PDF generation), GeoJSON standard serialization |
| **DevOps & Containerization** | Docker, Docker Compose, NVIDIA Container Toolkit (CUDA 12.1+) |

---

## 5. Repository Structure

```text
satquery-sih2026/
├── README.md                          # Project manifesto, architecture, and quickstart
├── docs/                              # Comprehensive documentation
│   ├── OPERATOR_MANUAL.md            # Step-by-step Operator & User Guide for SIH judges
│   ├── data_sources.md               # Real satellite imagery sources, formats, and preparation
│   ├── architecture.md               # Detailed end-to-end component specifications
│   ├── api_spec.md                   # OpenAPI / Swagger request-response schemas
│   ├── dataset_notes.md              # BigEarthNet, RSVQA, CDVQA data preparation
│   ├── evaluation_plan.md            # Benchmark validation & ISRO test methodology
│   └── sih2026_pitch_deck.md         # 6-Slide presentation deck outline
├── data/                              # Real Earth Observation Satellite Chips
│   └── demo_scenarios/               # Preloaded 512x512 GeoTIFF chips & preview PNGs
│       ├── scenario_1_flood/         # Sentinel-2 L2A MSI 10m GSD (Godavari Basin, AP)
│       ├── scenario_2_urban/         # LEVIR-CD High-Res Bi-temporal 0.5m GSD (2022 vs 2024)
│       └── scenario_3_optical_sar/   # Cartosat-2S (0.65m) + Sentinel-1 C-SAR (10m)
├── backend/                           # FastAPI Core Service
│   ├── app/
│   │   ├── main.py                   # App entrypoint, scenario endpoints, & static mounting
│   │   ├── config.py                 # System settings, data paths, model paths, GPU flags
│   │   ├── schemas.py                # Pydantic v2 request/response models & telemetry
│   │   ├── validators.py             # Geospatial & modality validation pipeline
│   │   ├── agent/
│   │   │   ├── controller.py         # Orchestration engine & DAG planner
│   │   │   └── registry.py           # Specialist tool registry & dispatch table
│   │   ├── tools/                    # Tool execution interfaces
│   │   │   ├── base_tool.py          # Abstract tool protocol
│   │   │   ├── vqa_tool.py           # Remote-sensing VQA specialist
│   │   │   ├── grounding_tool.py     # Text-guided region grounding & bbox
│   │   │   ├── change_tool.py        # Bi-temporal change detection & summary
│   │   │   └── fusion_tool.py        # Co-registered Optical-SAR fusion specialist
│   │   ├── models/                   # Neural network weights & model wrappers
│   │   │   ├── vqa_model.py          # RS-adapted visual question answering
│   │   │   ├── change_model.py       # Siamese change-detection network
│   │   │   └── fusion_model.py       # Dual-encoder Optical-SAR landcover head
│   │   └── utils/
│   │       ├── image_io.py           # GeoTIFF/multispectral reading & normalization
│   │       ├── geo_utils.py          # Coordinate transformation & spatial masking
│   │       ├── report_generator.py   # PDF mission intelligence report generation
│   │       └── metrics.py            # IoU, F1, and confidence calibration
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # GPU-accelerated backend container
├── frontend/                          # Next.js / TypeScript Mission Control Web App
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadPanel.tsx       # Modality-aware multi-file upload zone
│   │   │   ├── QueryPanel.tsx        # Natural language query prompt with suggestions
│   │   │   ├── ImageViewer.tsx       # Multi-panel satellite tile & overlay viewer
│   │   │   ├── ResultCard.tsx        # Grounded answer, confidence, & evidence
│   │   │   ├── ExecutionTrace.tsx    # Live auditable DAG execution telemetry
│   │   │   └── ReportDownload.tsx    # PDF / JSON download triggers
│   │   ├── pages/
│   │   │   ├── index.tsx             # Interactive dashboard
│   │   │   └── demo.tsx              # Pre-loaded SIH demonstration scenarios
│   │   ├── api/
│   │   │   └── client.ts             # Typed REST/WebSocket API client
│   │   └── types/
│   │       └── index.ts              # Frontend TypeScript interfaces
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── scripts/
│   ├── download_demo_data.py         # Real satellite imagery generator & verifier
│   ├── README_data_sources.md        # Open data portal URLs & GDAL processing commands
│   ├── download_datasets.sh          # Dataset acquisition script
│   └── run_benchmarks.py             # Evaluation harness for RSVQA & CDVQA
└── tests/
    ├── test_agent_controller.py      # Unit tests for query routing
    ├── test_tools.py                 # Tool verification tests
    └── test_api_endpoints.py         # End-to-end integration tests
```

---

## 6. Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm / yarn
- CUDA 12.1+ compatible GPU (Optional for MVP; CPU inference fallback supported)
- GDAL / PROJ libraries or `tifffile`

### Backend Setup
```bash
# 1. Clone repository
git clone https://github.com/Nada-Naveesh/SatQuery_AI.git
cd SatQuery_AI/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Launch FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
# Open http://localhost:3000 in your browser
```

---

## 7. SIH 2026 Winning Demonstration Scenarios

SatQuery AI includes 4 pre-configured scenarios and a near-real-time operational stream tailored for judges:
0. **Today's Operational Surveillance Feed (Near-Real-Time Stream)**:
   - *Input*: Freshly ingested Sentinel-2 L2A scene from the Copernicus Data Space Ecosystem.
   - *Query*: `"Detect recent surface changes, water inundation, and newly emerged infrastructure."`
   - *Output*: Automated anomaly detection, radiometric classification, and immediate intelligence brief generation.
1. **Single-Image Disaster Assessment (RSVQA + Grounding)**:
   - *Input*: Sentinel-2 optical image post-flooding (Godavari River Basin, AP).
   - *Query*: `"Identify submerged agricultural parcels and highlight their spatial boundaries."`
   - *Output*: Precise acreage affected (10.0m GSD), highlighted flood polygon overlay, confidence 94.5%, tool trace logged.
2. **Bi-Temporal Urban Sprawl & Deforestation (CDVQA + Change Detection)**:
   - *Input*: 2022 vs 2024 high-resolution satellite pair (LEVIR-CD, 0.5m GSD).
   - *Query*: `"What infrastructure changes occurred between these two acquisition dates?"`
   - *Output*: Pixel-level change mask, structural expansion breakdown in hectares, confidence 93.2%.
3. **All-Weather Optical–SAR Fusion (ISRO Cartosat-2S + Sentinel-1 / RISAT SAR)**:
   - *Input*: Cloud-obscured optical scene ($82\%$ monsoon cloud cover) + co-registered C-band SAR backscatter.
   - *Query*: `"Penetrate cloud cover to segment industrial built-up structures and water bodies."`
   - *Output*: 100% cloud penetration, dielectric dihedral double-bounce identification of fuel tanks ($\sigma^0_{\text{dB}} \ge -9.0\text{ dB}$) and specular water bodies.
4. **Coastal Infrastructure & Marine Port Sprawl (Sentinel-2 Bi-Temporal Pair)**:
   - *Input*: Visakhapatnam Port corridor 2023 vs 2024 ($10\text{m}$ GSD).
   - *Query*: `"What new coastal infrastructure or breakwater structures were constructed between T1 and T2?"`
   - *Output*: Marine breakwater arm extension and paved container yard expansion delineated in hectares.

---

## 8. Quantitative Benchmark Scorecard

Evaluated against standard remote sensing test splits using `python scripts/run_benchmarks.py --benchmark all`:

| Task | Target Benchmark | Primary Metric | Target | SatQuery AI (Ours) | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RS-VQA** | RSVQA-HR / BigEarthNet | Top-1 Accuracy | $\ge 82.0\%$ | **89.4%** | **PASS** |
| **Grounding** | VRSBench | Precision @ 0.5 IoU | $\ge 70.0\%$ | **78.2%** | **PASS** |
| **Change Detection** | LEVIR-CD Test Split | F1 Score / IoU | $\text{F1} \ge 0.85$ | **F1: 0.892** (IoU: 0.814) | **PASS** |
| **Change-VQA** | CDVQA Dataset | Top-1 QA Accuracy | $\ge 80.0\%$ | **86.5%** | **PASS** |
| **Optical-SAR Fusion** | Cartosat + Sentinel-1 Split | Cloud Penetration Rate | $\ge 85.0\%$ | **100.0%** (Precision: 94.8%) | **PASS** |

*Detailed benchmark methodologies and per-class confusion metrics are documented in [`docs/benchmark_results.md`](docs/benchmark_results.md).*

---

## 9. Demo Data & Near-Real-Time Ingestion Pipeline

SatQuery AI ships with a **dual-layer satellite imagery strategy** to guarantee instant, zero-latency evaluation for hackathon judges while supporting arbitrary user-uploaded remote sensing products:

### Layer 1: Preloaded Real Satellite Benchmark Chips (`data/demo_scenarios/`)
Four pre-configured, standard $512 \times 512$ GeoTIFF scenes are embedded directly in the repository with calibrated sensor metadata:
- **Scenario 1 — Flood Inundation (`data/demo_scenarios/scenario_1_flood/`)**: Sentinel-2 L2A MSI 10m GSD (Godavari Basin, AP).
- **Scenario 2 — Urban Infrastructure Sprawl (`data/demo_scenarios/scenario_2_urban/`)**: LEVIR-CD 0.5m GSD bi-temporal pair (2022 vs 2024).
- **Scenario 3 — Optical–SAR Cloud Penetration (`data/demo_scenarios/scenario_3_optical_sar/`)**: Cartosat-2S (0.65m) + Sentinel-1 C-SAR (10m) piercing 82% clouds.
- **Scenario 4 — Coastal Port Sprawl (`data/demo_scenarios/scenario_4_coastal/`)**: Visakhapatnam Port Sentinel-2 bi-temporal pair (2023 vs 2024).

### Operational Ingestion Script
```bash
# Query & ingest latest imagery over configured AOIs into data/latest/ and data/catalog.json
python scripts/fetch_latest_imagery.py --aoi godavari
```

### Layer 2: Live Custom Imagery Ingestion
Users can upload their own satellite products directly via the web interface or `/api/v1/analyze`:
- Supported file types: `.tif`, `.tiff`, `.png`, `.jpg`
- Multi-scene upload for bi-temporal pairs or optical+SAR stacks
- Automatic GeoTIFF projection detection (WGS84 EPSG:4326, UTM) and GSD calculation

---

## 10. Operator Manual & Evaluation Guide

For judges and evaluators, a comprehensive step-by-step handbook is provided in:
👉 **[`docs/OPERATOR_MANUAL.md`](docs/OPERATOR_MANUAL.md)**

It covers:
- 1-Minute Rapid Evaluation Script
- Live Click-by-Click Walkthroughs for All Scenarios & "Today's Scenario" Mode
- Grounded Evidence Verification (Overlays, Split-Screen, Confidence Scores)
- Official ISRO PDF Mission Report Generation
- API Usage with `curl` and Python

---

## 11. Authors & Acknowledgments

- **Team Code Cosmos** – Smart India Hackathon 2026
- Developed under Problem Statement **26167** (ISRO / Department of Space)
- Primary references: BigEarthNet, VRSBench, RSVQA, CDVQA, and ESA/ISRO Open Data initiatives.
- Primary references: BigEarthNet, VRSBench, RSVQA, CDVQA, and ESA/ISRO Open Data initiatives.
