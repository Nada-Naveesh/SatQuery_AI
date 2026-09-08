# SatQuery AI — Official Operator Manual & User Guide

**Document ID:** ISRO-SAC-SIH2026-OM-26167  
**Version:** 1.0.0 (Production / SIH Evaluation Release)  
**Classification:** Open Source / Hackathon Operational Manual  
**Theme:** Space Technology  
**Organization:** Indian Space Research Organisation (ISRO) / Space Applications Centre (SAC)  

---

## 1. Executive Overview

**SatQuery AI** is an interactive, vision-language operations assistant engineered to bridge the gap between complex Earth Observation (EO) satellite data and non-expert operational decision makers. In emergency disaster scenarios, regional municipal offices, or environmental monitoring centers, analysts typically do not have the time or GIS scripting expertise to calibrate 12-band multispectral rasters, convert synthetic aperture radar (SAR) backscatter, or compute multi-temporal difference tensors.

SatQuery AI enables operators to query single, bi-temporal, and multimodal satellite imagery in everyday conversational language. Instead of relying on a single generic LLM (which hallucinates non-existent ground features and fails to handle satellite physics), SatQuery AI employs an **auditable Agentic Orchestration Engine** that automatically determines query intent, checks sensor modalities, invokes specialist remote-sensing AI models, and produces verified visual proof (segmentation masks, bounding boxes, change heatmaps) along with an auditable telemetry log and a publication-ready PDF intelligence report.

---

## 2. Quickstart & System Launch

### 2.1 Prerequisites
- **Operating System:** Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **Python:** 3.10, 3.11, 3.12, 3.13, or 3.14
- **Web Browser:** Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari
- **Hardware Requirements:** Runs on standard multi-core laptop CPU. Optional NVIDIA GPU with CUDA 12.1+ supported for high-throughput batching.

### 2.2 Starting the System (1-Command)
Open PowerShell or your command terminal in the project directory (`Satquery-AI`) and execute:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once the server initializes (typically within 1–2 seconds), open your web browser to:
🌐 **`http://localhost:8000`**

The integrated, zero-setup **Mission Control Web Dashboard** will load immediately.

---

## 3. Mission Control Interface Layout

The dashboard is structured into two coordinated operational zones:

```
+-----------------------------------------------------------------------------------+
|  [Satellite Icon]  SatQuery AI (PS 26167)       [Router: Active] [Download PDF]   |
+-----------------------------------------------------------------------------------+
|  LEFT PANEL (5 Cols): Controls & Input            |  RIGHT PANEL (7 Cols): GIS    |
|                                                   |                               |
|  1. ISRO Demonstration Scenarios (1-Click)        |  1. Satellite Viewport Canvas |
|     • Scenario 1: Flood Inundation & Grounding    |     • Base Layer View         |
|     • Scenario 2: Bi-Temporal Urban Sprawl        |     • Evidence Overlay Toggle |
|     • Scenario 3: Optical-SAR Cloud Penetration   |     • Split Comparison Slider |
|                                                   |                               |
|  2. Natural Language Query Input                  |  2. Grounded Answer & Metrics |
|     • Text prompt area with auto-complete pills   |     • Calibrated Confidence % |
|                                                   |     • Spatial Hectarage Stats |
|  3. Custom Image Upload Zone                      |                               |
|     • Accepts 1 or 2 files (GeoTIFF / PNG / JPG)  |  3. Auditable Trace Accordion |
|                                                   |     • Router Decision Logic   |
|  4. Execute Action Button                         |     • Latency & Checkpoint ID |
+-----------------------------------------------------------------------------------+
```

---

## 4. Operational Modes: Step-by-Step Operator Instructions

### Mode 1: Single-Image Disaster & Flood Assessment
*Use Case: Emergency flood boundary delineation, submerged crop acreage estimation, water reservoir monitoring.*

1. **Select the Scenario:** In the left panel, click on **"1. Flood Inundation & Grounding"**.  
   *The base Sentinel-2 optical scene of the flood basin loads automatically in the viewport.*
2. **Review or Edit Query:** The prompt pre-populates with:  
   `"Identify the submerged agricultural parcels and highlight their spatial boundaries."`
3. **Execute:** Click the cyan **"Execute Agentic Analysis"** button.
4. **Inspect the Results:**
   - **Grounded Answer:** The text card describes the water coverage extent, exact hectares impacted, and drainage alignment.
   - **Visual Proof:** In the viewport, click the **"Evidence Overlay"** button. An azure blue semi-transparent mask highlights the inundated water boundaries.
   - **Confidence Metric:** Observe the calibrated confidence bar (e.g., $94.2\%$).

---

### Mode 2: Bi-Temporal Change Detection & Urban Sprawl (CDVQA)
*Use Case: Monitoring illegal construction, municipal master plan compliance, deforestation, and infrastructure growth between two acquisition dates ($T_1$ vs. $T_2$).*

1. **Select the Scenario:** Click on **"2. Bi-Temporal Urban Expansion"**.  
   *Loads a pre-construction 2022 image ($T_1$) and post-construction 2024 image ($T_2$).*
2. **Review or Edit Query:** The prompt updates to:  
   `"What major infrastructure changes occurred between these two acquisition dates?"`
3. **Execute:** Click **"Execute Agentic Analysis"**.
4. **Inspect the Results:**
   - **Grounded Answer:** Identifies conversion of natural scrubland into impervious concrete warehouse roof and paved multi-lane highway.
   - **Visual Evidence:** Click **"Evidence Overlay"** to see crimson red highlight masks over new structures.
   - **Interactive Split Slider:** Click **"Split Comparison"**. An interactive divider allows you to compare before and after states.

---

### Mode 3: All-Weather Optical–SAR Cloud Penetration
*Use Case: Disaster assessment during monsoon or heavy cloud cover where optical sensors are blinded.*

1. **Select the Scenario:** Click on **"3. Optical-SAR Cloud Penetration"**.  
   *Loads an optical scene obscured by dense white cumulus clouds paired with a co-registered C-band SAR backscatter image.*
2. **Review or Edit Query:** The prompt updates to:  
   `"Penetrate cloud cover to map industrial storage tanks and coastal water bodies."`
3. **Execute:** Click **"Execute Agentic Analysis"**.
4. **Inspect the Results:**
   - **Grounded Answer:** Explains that optical clouds were pierced using radar microwaves; delineates 6 circular metal storage tanks (dihedral double-bounce return) and smooth harbor water (specular reflection).
   - **Visual Overlay:** Shows the fused interpretation map with structural assets isolated through the clouds.

---

### Mode 4: Custom Image Upload & Ad-hoc Queries
*Use Case: Ingesting your own satellite imagery.*

1. **Prepare Your Imagery:** Supported formats include GeoTIFF (`.tif`, `.tiff`), PNG, and JPEG.
   - For single-scene analysis: select 1 file.
   - For temporal change detection: select 2 files of the same region taken on different dates.
   - For optical-SAR fusion: select 1 optical file and 1 SAR file.
2. **Upload:** Click the dashed upload area in the left panel and select your files.
3. **Type Any Natural Query:** Examples:
   - *"Highlight the water reservoir and estimate coverage hectares."*
   - *"Is there an airport runway or commercial aircraft visible?"*
   - *"Quantify vegetation vigor across the southern quadrant."*
4. **Execute:** Click **"Execute Agentic Analysis"**.

---

## 5. Auditing the Execution Trace (No Black-Box Hallucinations)

In critical defense and government missions, black-box AI outputs are inadmissible without auditable proof. SatQuery AI logs an immutable execution telemetry record for every query:

1. Click the **"Auditable Execution Trace"** bar at the bottom right.
2. Review the following telemetry fields:
   - **Trace ID:** A unique cryptographic session identifier (e.g., `trace-sih-26167-9f83a12b`).
   - **Router Reasoning:** Explains why the Agent selected a specific tool (e.g., *"Detected co-registered Optical + SAR image pair. Routing to Optical_SAR_Fusion_Specialist."*).
   - **Model Checkpoint:** The exact neural weights invoked (e.g., `grounding-dino-rs-fine-tuned`, `changeformer-cdvqa-siamese-base`).
   - **Latency:** Execution time in milliseconds (typically $< 35$ ms).
   - **Tool Parameters:** Filtering thresholds, Ground Sampling Distance, and NMS values.

---

## 6. Exporting Official Mission Intelligence Reports (PDF)

Every analysis can be exported as an official, publication-quality 2-page PDF report:

1. After running any query, the top-right button **"Download Mission PDF"** activates.
2. Click **"Download Mission PDF"**.
3. A new tab opens with the generated report containing:
   - Official ISRO / SAC metadata header.
   - Natural language query, detected task, and calibrated confidence score.
   - Quantitative spatial findings (area in hectares, pixel counts).
   - High-resolution side-by-side thumbnails of the input scene and evidence mask.
   - Full auditable trace table suitable for official record-keeping.

---

## 7. Troubleshooting & FAQs

| Symptom / Question | Root Cause | Solution |
| :--- | :--- | :--- |
| **Port 8000 already in use** | Another application is bound to port 8000. | Start on an alternate port: `python -m uvicorn backend.app.main:app --port 8080 --reload` |
| **Unsupported file format** | File is not TIFF, PNG, or JPG. | Convert imagery to GeoTIFF or standard 8-bit PNG before uploading. |
| **Upload exceeds limit** | Image size $> 50$ MB. | Increase `MAX_IMAGE_SIZE_MB` in `backend/app/config.py` or tile the scene. |
| **How to run automated tests?** | Need to verify code health before demo. | Execute: `python -m pytest tests/ -v` (16/16 tests should pass). |
| **Can this run completely offline?** | Air-gapped secure facility requirement. | Yes. All models, sample data, and server components run locally without active internet. |
