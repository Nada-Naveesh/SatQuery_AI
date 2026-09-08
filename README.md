# SatQuery AI: Interactive Vision-Language Assistant for Multimodal Remote Sensing

[![SIH 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://sih.gov.in)
[![Problem Statement](https://img.shields.io/badge/PS%20ID-26167-blue.svg)](https://sih.gov.in)
[![Organization](https://img.shields.io/badge/Organization-ISRO%20%2F%20SAC-success.svg)](https://www.isro.gov.in)
[![Theme](https://img.shields.io/badge/Theme-Space%20Technology-purple.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)]()

> **"From raw satellite pixels to verified, auditable intelligence in a single natural language query."**

📘 **Quick Links:** [Official Operator Manual & User Guide (Step-by-Step Instructions)](docs/OPERATOR_MANUAL.md) | [SIH 6-Slide Pitch Deck](docs/sih2026_pitch_deck.md) | [Architecture Specification](docs/architecture.md) | [API Contracts](docs/api_spec.md)

---

## 1. Executive Summary

**SatQuery AI** is an evidence-grounded, agentic remote-sensing operations assistant engineered for **Smart India Hackathon 2026 (Problem Statement ID: 26167)** under the **ISRO / Department of Space** theme. Traditional satellite data exploitation requires domain expertise in geographic information systems (GIS), multi-band sensor calibration, and specialized computer vision pipelines. SatQuery AI democratizes satellite imagery analysis by allowing non-expert decision makers, disaster response commanders, and urban planners to interrogate single, multispectral, Synthetic Aperture Radar (SAR), and multitemporal satellite data using everyday natural language.

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
│   ├── architecture.md               # Detailed end-to-end component specifications
│   ├── api_spec.md                   # OpenAPI / Swagger request-response schemas
│   ├── dataset_notes.md              # BigEarthNet, RSVQA, CDVQA data preparation
│   ├── evaluation_plan.md            # Benchmark validation & ISRO test methodology
│   └── sih2026_pitch_deck.md         # 6-Slide presentation deck outline
├── backend/                           # FastAPI Core Service
│   ├── app/
│   │   ├── main.py                   # App entrypoint & middleware configuration
│   │   ├── config.py                 # System settings, model paths, GPU flags
│   │   ├── schemas.py                # Pydantic v2 request/response models
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
├── notebooks/                         # Research & Adaptation Notebooks
│   ├── data_exploration.ipynb        # BigEarthNet-S1/S2 EDA
│   ├── model_finetuning_bigearthnet.ipynb # LoRA fine-tuning for RS-VQA
│   └── benchmark_evaluation.ipynb    # Accuracy & IoU metrics on public test splits
├── scripts/
│   ├── download_datasets.sh          # Sample dataset acquisition script
│   ├── run_benchmarks.py             # Evaluation harness for RSVQA & CDVQA
│   └── generate_sample_data.py       # Synthetic test pair generator for offline demo
└── tests/
    ├── test_agent_controller.py      # Unit tests for query routing
    ├── test_tools.py                 # Tool verification tests
    └── test_api_endpoints.py         # End-to-end integration tests
```

---

## 6. Quickstart Guide

### Prerequisites
- Python 3.10 or 3.11
- Node.js 18+ and npm / yarn
- CUDA 12.1+ compatible GPU (Optional for MVP; CPU inference fallback supported)
- GDAL / PROJ libraries (`libgdal-dev`)

### Backend Setup
```bash
# 1. Clone repository
git clone https://github.com/your-team/satquery-sih2026.git
cd satquery-sih2026/backend

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

SatQuery AI includes 3 pre-configured scenarios tailored for judges:
1. **Single-Image Disaster Assessment (RSVQA + Grounding)**:
   - *Input*: Sentinel-2 optical image post-flooding.
   - *Query*: `"Identify submerged agricultural parcels and quantify flood extent."`
   - *Output*: Precise acreage affected, highlighted flood polygon overlay, confidence 94.2%, tool trace logged.
2. **Bi-Temporal Urban Sprawl & Deforestation (CDVQA + Change Detection)**:
   - *Input*: 2022 vs 2024 Sentinel-2 image pair.
   - *Query*: `"What infrastructure changes occurred between these two acquisition dates?"`
   - *Output*: Pixel-level change mask, structural expansion breakdown, confidence 91.8%.
3. **All-Weather Optical–SAR Fusion (ISRO Cartosat-2S + RISAT SAR)**:
   - *Input*: Cloud-obscured optical scene + co-registered C-band SAR backscatter.
   - *Query*: `"Penetrate cloud cover to segment industrial built-up structures and water bodies."`
   - *Output*: Fused feature classification proving SAR structural penetration through cloud occlusion.

---

## 8. Authors & Acknowledgments

- **Team SatQuery AI** – Smart India Hackathon 2026
- Developed under Problem Statement **26167** (ISRO / Department of Space)
- Primary references: BigEarthNet, VRSBench, RSVQA, CDVQA, and ESA/ISRO Open Data initiatives.
