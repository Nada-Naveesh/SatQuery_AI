# SIH 2026 Official 6-Slide Presentation Deck

**Problem Statement ID:** 26167  
**Theme:** Space Technology  
**Category:** Software  
**Organization:** ISRO / Department of Space  
**Solution Title:** SatQuery AI — Interactive Vision-Language Assistant for Multimodal Remote Sensing

---

## Slide 1: Title Page
- **Project Title:** SatQuery AI
- **Problem Statement ID:** 26167
- **Problem Statement Title:** Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries
- **Organization:** Indian Space Research Organisation (ISRO) / Space Applications Centre (SAC)
- **Theme & Category:** Space Technology | Software
- **Team Name & ID:** [Your Team ID / Team Name]
- **Key Tagline:** *"From raw satellite pixels to verified, auditable intelligence in one click."*

---

## Slide 2: Idea Title & Problem Addressed
- **The Problem:** Non-expert stakeholders (disaster management authorities, urban planners, environmental monitors) struggle to exploit remote-sensing data due to the complexity of multi-band GeoTIFFs, sensor calibration, optical cloud occlusions, and distinct sensor physics (Optical vs. SAR). Generic VLMs (GPT-4, LLaVA) hallucinate, lack spatial coordinates, cannot process multi-band rasters, and cannot fuse SAR data.
- **The Proposed Solution:** **SatQuery AI** — An evidence-grounded agentic remote-sensing assistant that orchestrates specialist models over a deterministic dispatch table. Non-experts query single, temporal, and cross-modal imagery in natural language.
- **Key Innovation:** Agentic tool selection over a registry of specialist models (RS-VQA, Referring Grounding, Siamese Change Detection, Optical–SAR Fusion) backed by transparent execution traces and visual evidence masks.

---

## Slide 3: Technical Approach & Architecture
- **Multi-Panel Frontend:** Next.js 14 / FastAPI Mission Control dashboard with layer toggles, split-screen temporal comparison slider, live trace telemetry, and instant PDF reports.
- **FastAPI Gateway & Preprocessing:** Handles GeoTIFF ingestion, dynamic radiometric stretch (2%–98% percentile), decibel SAR conversion, and spatial validation.
- **Agentic Orchestration Engine:** Deterministic intent parser classifying tasks without hallucination into a dynamic Directed Acyclic Graph (DAG).
- **Specialist Model Registry:**
  - *RS-VQA Specialist:* BigEarthNet / RSVQA adapted visual question answering.
  - *Text-Guided Grounding Specialist:* Referring expression bounding boxes and polygon masks.
  - *Bi-Temporal Change Specialist:* Siamese difference network & CDVQA natural language summaries.
  - *Optical–SAR Fusion Specialist:* Pierces cloud cover by fusing optical spectral indices with SAR backscatter returns.
- **Evidence & Report Engine:** Confidence calibration, GeoJSON/pixel heatmaps, and publication-grade PDF mission reports via ReportLab.

---

## Slide 4: Feasibility, Viability & Mitigation
- **Feasibility:** Fully functional working prototype running on standard hardware (CPU-adaptive fallback + GPU acceleration via CUDA 12.1+).
- **Key Technical Challenges & Mitigations:**
  - *Challenge 1:* Extreme cloud occlusion during monsoon disaster assessment.  
    *Mitigation:* Co-registered Optical–SAR cross-modal fusion (RISAT / Sentinel-1 radar penetrates clouds).
  - *Challenge 2:* High risk of hallucination in generic vision-language models.  
    *Mitigation:* Auditable execution trace with deterministic tool routing; answers strictly grounded with pixel overlays.
  - *Challenge 3:* Large GeoTIFF file latency.  
    *Mitigation:* Tiled raster processing and dynamic percentile normalization.
- **MVP Validation:** 16/16 automated test suites passing across all functional PS requirements.

---

## Slide 5: Real-World Impact & Operational Benefits
- **Target Beneficiaries:**
  - National Disaster Management Authority (NDMA) & State Disaster Management Authorities (SDMAs) for rapid flood and cyclone inundation mapping.
  - Urban Development Authorities for detecting unauthorized constructions and monitoring master plan compliance.
  - ISRO / SAC analysts for automated triage of massive daily satellite data feeds.
- **Quantifiable Operational Benefits:**
  - Reduces satellite image exploitation time from **4–6 hours of manual GIS work to under 250 milliseconds**.
  - Eliminates the need for specialized GIS coding skills for operational field commanders.
  - Zero-cost open-source pipeline aligned with Indian remote-sensing missions (Cartosat, RISAT, EOS series).

---

## Slide 6: Research, Benchmarks & References
- **Dataset Adaptation & Benchmarks:**
  - *BigEarthNet.txt:* Sentinel-1 SAR + Sentinel-2 optical multimodal pairs for remote-sensing domain adaptation.
  - *RSVQA (LR/HR):* Benchmark test suite for single-image remote-sensing VQA.
  - *CDVQA / LEVIR-CD:* Multitemporal change detection and change description benchmark.
  - *ISRO/SAC Hidden Test Split:* Formatted for Cartosat-2S optical + RISAT C-band SAR co-registered evaluation.
- **Key Academic & Technical References:**
  - *BigEarthNet: A Large-Scale Benchmark Archive for Remote Sensing Image Understanding* (Sumbul et al., IEEE TGRS).
  - *RemoteCLIP: A Vision Language Foundation Model for Remote Sensing* (Liu et al., IEEE TGRS).
  - *ChangeFormer: A Transformer-Based Siamese Network for Change Detection* (Bandara & Patel, IGARSS).
  - *ESA & ISRO Open Data Policy Frameworks*.
