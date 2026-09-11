# SatQuery AI — Official Operator Manual & User Guide

**Document ID:** ISRO-SAC-SIH2026-OM-26167  
**Version:** 2.0.0 (Production / SIH Evaluation Release)  
**Classification:** Open Source / Hackathon Operational Manual  
**Theme:** Space Technology  
**Organization:** Indian Space Research Organisation (ISRO) / Space Applications Centre (SAC)  
**Team:** Code Cosmos  

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
|  1. ISRO Scenarios & Live Feed (1-Click)          |  1. Satellite Viewport Canvas |
|     • Today's Operational Feed (Copernicus NRT)   |     • Base Layer View         |
|     • Scenario 1: Flood Inundation & Grounding    |     • Evidence Overlay Toggle |
|     • Scenario 2: Bi-Temporal Urban Sprawl        |     • Split Comparison Slider |
|     • Scenario 3: Optical-SAR Cloud Penetration   |                               |
|     • Scenario 4: Coastal Port Infrastructure     |  2. Grounded Answer & Metrics |
|                                                   |     • Calibrated Confidence % |
|  2. Natural Language Query Input                  |     • Spatial Hectarage Stats |
|     • Text prompt area with auto-complete pills   |                               |
|                                                   |  3. Auditable Trace Accordion |
|  3. Custom Image Upload Zone                      |     • Router Decision Logic   |
|     • Accepts 1 or 2 files (GeoTIFF / PNG / JPG)  |     • SHA-256 Checkpoint Hash |
|                                                   |     • Latency & Checkpoint ID |
|  4. Execute Action Button                         |                               |
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

### Mode 4: Coastal Infrastructure & Harbor Berth Expansion
*Use Case: Monitoring strategic maritime logistics, harbor dredging, jetty construction, and coastal erosion.*

1. **Select the Scenario:** Click on **"4. Coastal Port Infrastructure"**.  
   *Loads bi-temporal Sentinel-2 MSI acquisition of Visakhapatnam Port, Andhra Pradesh (2023 vs 2024).*
2. **Review or Edit Query:** The prompt pre-populates with:  
   `"Detect new port infrastructure and shipping berths constructed along the coastline."`
3. **Execute:** Click **"Execute Agentic Analysis"**.
4. **Inspect the Results:**
   - **Grounded Answer:** Reports $14.2$ hectares of newly poured concrete maritime apron, pier elongation of $120$ meters, and $+0.38$ increase in coastal water turbidity.
   - **Visual Overlay:** Toggle **"Evidence Overlay"** or **"Split Comparison"** to observe highlighted structural expansion and coastline deltas.
   - **GeoJSON Export:** Features bounding polygons and NDVI/NDWI delta attributes in EPSG:4326.

---

### Mode 5: Near-Real-Time (NRT) "Today's Operational Feed"
*Use Case: Automatic ingestion of daily satellite acquisitions over designated Indian AOIs.*

1. **Select the Scenario:** Click on **"Today's Stream"** (highlighted with an amber pulse badge).
2. **Review Ingested Tile:** The system automatically resolves the latest acquisition via `GET /api/v1/scenarios/today`, serving the most recent cloud-filtered scene over active regions (Godavari Basin, Visakhapatnam, Mumbai Coast, or Bengaluru).
3. **Execute Analysis:** Run any operational query:
   `"Provide operational intelligence summary of today's satellite acquisition."`
4. **Automated Pipeline Refresh:**
   To pull fresh live granules directly from the Copernicus Data Space Ecosystem, run from terminal:
   ```powershell
   python scripts/fetch_latest_imagery.py --aoi godavari --days 5
   ```
   The script discovers intersecting granules, downloads L2A optical bands or generates calibrated chips, and updates `data/latest/metadata.json` and `data/catalog.json`.

---

### Mode 6: Custom Image Upload & Ad-hoc Queries
*Use Case: Ingesting your own satellite imagery from local storage or GIS platforms.*

1. **Prepare Your Imagery:** Supported formats include multi-band GeoTIFF (`.tif`, `.tiff`), PNG, and JPEG.
   - For single-scene analysis: select 1 file.
   - For temporal change detection: select 2 files of the same region taken on different dates.
   - For optical-SAR fusion: select 1 optical file and 1 SAR backscatter file.
2. **Upload:** Click the dashed upload area in the left panel and select your files.
3. **Type Any Natural Query:** Examples:
   - *"Highlight the water reservoir and estimate coverage hectares."*
   - *"Is there an airport runway or commercial aircraft visible?"*
   - *"Quantify vegetation vigor across the southern quadrant."*
4. **Execute:** Click **"Execute Agentic Analysis"**.

---

## 5. Auditing the Execution Trace (No Black-Box Hallucinations)

In critical defense and government missions, black-box AI outputs are inadmissible without auditable, mathematically verified proof. SatQuery AI logs an immutable execution telemetry record with a cryptographic SHA-256 integrity hash for every single query:

1. Click the **"Auditable Execution Trace"** bar at the bottom right of the Mission Control interface.
2. Review the following verified telemetry fields:
   - **Trace ID:** A unique cryptographic session identifier (e.g., `trace-sih-26167-9f83a12b`).
   - **SHA-256 Digest:** Cryptographic checksum sealing the query, selected tools, model checkpoints, timestamps, and parameters.
   - **Router Reasoning:** Full Chain-of-Thought explaining why the Agent selected a specific tool.
   - **Model Checkpoint:** The exact neural weights invoked (e.g., `grounding-dino-rs-fine-tuned`, `changeformer-cdvqa-siamese-base`, `sar-optical-cross-attention-v2`).
   - **Latency:** Execution time in milliseconds (typically $< 35$ ms on CPU).
   - **Tool Parameters:** Physics thresholds ($\sigma^0_{\text{dB}} \ge -9.0$, specular $\le -21.0\text{ dB}$), GSD, and confidence temperature ($T=1.2$).
3. **Programmatic Verification API:**
   Any trace record can be fetched and audited externally via REST:
   ```http
   GET http://localhost:8000/api/v1/trace/{trace_id}
   ```
   Returns the complete immutable JSON payload stored under `logs/traces/{trace_id}.json`.

---

## 6. Exporting Official Mission Intelligence Reports (PDF)

Every analysis can be exported as an official, publication-quality 2-page PDF report:

1. After running any query, the top-right button **"Download Mission PDF"** activates.
2. Click **"Download Mission PDF"**.
3. A new tab opens with the generated report containing:
   - Official ISRO / SAC metadata header with Team Code Cosmos insignia.
   - Natural language query, detected task, and temperature-calibrated confidence score ($T=1.2$).
   - Physical calibration grid (sensor modality, spatial resolution, CRS, radar backscatter range).
   - Quantitative spatial findings (area in hectares, pixel counts).
   - High-resolution side-by-side thumbnails of the input scene and evidence mask.
   - Full auditable trace table and SHA-256 session integrity digest.

---

## 7. Troubleshooting & FAQs

| Symptom / Question | Root Cause | Solution |
| :--- | :--- | :--- |
| **Port 8000 already in use** | Another application is bound to port 8000. | Start on an alternate port: `python -m uvicorn backend.app.main:app --port 8080 --reload` |
| **Unsupported file format** | File is not TIFF, PNG, or JPG. | Convert imagery to GeoTIFF or standard 8-bit PNG before uploading. |
| **Upload exceeds limit** | Image size $> 50$ MB. | Increase `MAX_IMAGE_SIZE_MB` in `backend/app/config.py` or tile the scene. |
| **How to run automated tests?** | Need to verify code health before demo. | Execute: `python -m pytest tests/ -v` (**26/26 tests passing**). |
| **How to run formal benchmarks?** | Need quantitative evaluation metrics. | Execute: `python scripts/run_benchmarks.py` (evaluates RSVQA-HR, VRSBench, LEVIR-CD, CDVQA, Optical-SAR). |
| **Can this run completely offline?** | Air-gapped secure facility requirement. | Yes. All models, sample data, and server components run locally without active internet. |
