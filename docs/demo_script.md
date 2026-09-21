# SIH 2026 Judge Presentation & Live Demo Script

**Smart India Hackathon 2026 | Problem Statement ID: 26167**  
**Theme:** Space Technology | **ISRO / SAC**  
**Project:** SatQuery AI — Natural Language Satellite Intelligence & Evidence-Based Analysis Platform

---

## Presentation Overview & Time Allocation (Total: 6 - 8 Minutes)

| Act | Focus Area | Time | Key Takeaway for Judges |
| :--- | :--- | :--- | :--- |
| **Act 1** | Problem Statement & High-Level Architecture | 1.0 min | Overcoming the GIS barrier with an agentic, explainable remote sensing platform |
| **Act 2** | Scenario 1: Gudlavalleru Urban Growth (2025 vs 2026) | 1.5 min | Multi-band physical raster calculations, non-zero hectares, 4 interactive view modes |
| **Act 3** | Scenario 2 & 3: Coastal Infrastructure & Flood Inundation | 1.5 min | Real environmental and defense use cases (port dredging and flood disaster response) |
| **Act 4** | Live Location Search & Copernicus Ingestion | 1.5 min | Real-time Nominatim geocoding and live Copernicus CDSE Sentinel-2 STAC queries |
| **Act 5** | Auditable Execution Trace & Instant PDF Report | 1.0 min | Full defense-grade traceability, open JSON export, and identical PDF artifacts |
| **Act 6** | Judge Q&A & Technical Defense | 1.5 min | Mathematical rigor, atmospheric masking, MMU filtering, Optical+SAR fusion |

---

## Act 1: Problem & Vision (1 Minute)

> **Speaker Says:**
> *"Respected Judges, Problem Statement 26167 asks us to build an intelligent vision-language assistant for satellite imagery. Every day, gigabytes of Earth observation data are captured by ISRO and international constellations, but normal civil officers, emergency responders, and town planners cannot use them because interpreting 12-band GeoTIFFs requires specialized GIS software and deep remote sensing training.*
> 
> *Our solution is **SatQuery AI**: an agentic, evidence-based satellite analysis platform. You can ask any question in everyday English—like 'What changed here between 2025 and 2026?'—and our system runs genuine multi-band raster math ($\Delta\text{NDVI}, \Delta\text{NDWI}, \Delta\text{NDBI}$), visually highlights the calculated evidence on the map, calculates physical ground-truth hectares, and generates an auditable defense-grade PDF report in seconds.*
> 
> *Let me demonstrate this live."*

---

## Act 2: Scenario 1 — Gudlavalleru Urban Growth (1.5 Minutes)

1. **Point to the Dashboard:**
   > *"Notice our dark tactical Mission Control interface. On load, the platform has initialized our verified ground-truth competition package for Gudlavalleru, Krishna District, Andhra Pradesh.*
   > *Look at the Tactical Coordinates HUD in the top left of the viewport: Lat 16.0200° N, Lon 80.7000° E, BBox [15.98, 80.65, 16.08, 80.75]."*

2. **Run Analysis:**
   - Click the **Analyze Satellite Images** button.
   - The status spinner appears for ~300ms while the multi-band engine processes the rasters.

3. **Explain the Evidence Overlay:**
   > *"The AI agent detected this as a bi-temporal change detection task. Look closely at the viewport:*
   > *Every red pixel you see is not painted on with CSS. It is the result of real raster calculations: a positive increase in Normalized Difference Built-up Index ($\Delta\text{NDBI} > +0.20$) paired with vegetation loss ($\Delta\text{NDVI} < -0.10$), filtered through a Minimum Mapping Unit of 9 pixels to eliminate false-alarm noise.*
   > *In our Ground-Truth Physical Hectare Breakdown card below, we see exactly **242.1 hectares** of new built-up construction and paved roads."*

4. **Demonstrate the 4 View Modes & Interactive Sliders:**
   - Click **Base (T2)**: Shows the current 2026 satellite image.
   - Click **Evidence Overlay**: Restores the red change overlay.
   - Adjust the **Overlay Opacity Slider** from 85% to 40% and back: show that judges can see the underlying roads through the transparent calculated layer.
   - Click **Split Comparison**: Drag the central divider left and right across the canvas:
     > *"Judges, look at the interactive split wiper. As I slide across, you can visually confirm the exact boundary between 2025 farmland and 2026 paved development."*
   - Click **Quality View**:
     > *"This is our Atmospheric Quality View. Our engine validates that atmospheric transmission is 100% cloud-free, with sub-pixel co-registration, yielding an honest, calibrated confidence score of 94.0%."*

---

## Act 3: Scenarios 2 & 3 — Coastal Change & Flood Inundation (1.5 Minutes)

1. **Machilipatnam Deepwater Port:**
   - Click the **Machilipatnam** quick pill in the AP location bar.
   - Click **Analyze Satellite Images**.
   - Show the result:
     > *"Here at Machilipatnam Deepwater Port (16.19°N, 81.13°E), our system detects **158.3 hectares** of total change, specifically identifying 93.4 hectares of coastal breakwater construction and harbor dredging. Notice the plain-English narrative tailored specifically to maritime infrastructure."*

2. **Godavari River Monsoon Inundation:**
   - Click the **Godavari Flood** quick pill.
   - Click **Analyze Satellite Images**.
   - Show the result:
     > *"In this disaster response scenario over the Godavari Basin (17.00°N, 81.80°E), monsoon river swelling submerged agricultural parcels. The system calculated **627.5 hectares** of flood inundation highlighted in cyan blue using $\Delta\text{NDWI}$. An emergency collector can immediately know which revenue blocks require relief."*

---

## Act 4: Live Search & Copernicus CDSE Ingestion (1.5 Minutes)

> *"Judges might ask: 'Is your system limited only to pre-selected demo towns?' Absolutely not."*

1. **Search Any Place in Andhra Pradesh:**
   - In the **Search AP** box, type `Avanigadda` or `Vijayawada` and press **Enter**.
   - The HUD updates instantly with the coordinates of Avanigadda (Krishna Delta Estuary, 16.02°N, 80.92°E).

2. **Live Copernicus Data Space Ecosystem Search:**
   - Click the **Copernicus Live** tab.
   - Type any Indian city, e.g., `Vijayawada`.
   - Click **Search Copernicus**.
   - Watch the system query the live Copernicus API:
     > *"SatQuery AI geocoded Vijayawada via OpenStreetMap Nominatim, extracted the bounding box, and queried the European Space Agency's Copernicus Data Space Ecosystem for Sentinel-2 Level-2A products.*
     > *Look at the results: real Sentinel-2 product IDs, acquisition dates, cloud cover percentages, and image thumbnails.*
     > *Because we found both a 2025 and 2026 acquisition, the system automatically generated a **Bi-Temporal Pair Available** card. Clicking it loads both scenes directly into our multi-band raster pipeline!"*

---

## Act 5: Auditable Execution Trace & Defense PDF Report (1 Minute)

1. **Examine the Auditable Trace:**
   - Click the **Auditable Execution Trace & Telemetry** accordion.
   - Point out:
     - Trace ID (e.g., `trace_20260922_...`)
     - Router Reasoning: *"Bi-temporal multi-band optical pair provided... Routing to change_tool"*
     - Tool Execution Latency: `~300 ms`
     - Click **View Full Audit Trace (JSON)**: Show complete machine-readable audit trail that can be integrated into defense C4ISR pipelines.

2. **Generate the PDF Report:**
   - Click the red **PDF Report** button in the header.
   - A new browser tab opens with the freshly generated, print-ready PDF report:
     > *"Judges, look at the generated PDF report. It features the exact same calculated evidence overlay, the exact 242.1 hectare ground-truth breakdown, the satellite coordinate metadata, and a plain-English executive summary that any commanding officer or civil magistrate can immediately understand and act upon."*

---

## Act 6: Anticipated Judge Questions & Technical Answers

### Q1: "Are the colors on the map real or artificially generated?"
> **Answer:** *"They are 100% physical raster calculations. In `backend/app/processing/`, we extract individual Sentinel-2 bands—B02 Blue, B03 Green, B04 Red, and B08 NIR. We compute standard physical indices: $\text{NDVI}$, $\text{NDWI}$, and $\text{NDBI}$. A pixel is only colored red if its built-up index increased by $\Delta\text{NDBI} > +0.20$ and vegetation decreased by $\Delta\text{NDVI} < -0.10$. Furthermore, our Minimum Mapping Unit filter discards any noise clusters smaller than 9 contiguous pixels ($900\,\text{m}^2$)."*

### Q2: "How do you calculate hectares from satellite images?"
> **Answer:** *"Sentinel-2 MSI Level-2A imagery has a native 10-meter Ground Sampling Distance (GSD). That means one square pixel represents $10\text{m} \times 10\text{m} = 100\,\text{m}^2$. Since one hectare equals $10\,000\,\text{m}^2$, each pixel equals exactly $0.01\text{ hectares}$. By counting the classified pixels in our change mask, we obtain the exact physical area in hectares without any guesswork."*

### Q3: "How does your system handle cloud cover?"
> **Answer:** *"We employ two complementary safeguards: First, in `cloud_mask.py`, we apply a multi-band atmospheric filter ($B_{\text{blue}} > 0.80$, high brightness, and whiteness) that excludes cloudy pixels and scales down the confidence score. Second, when persistent monsoon clouds obscure an area, our Agentic Controller can route to the Optical+SAR Fusion Tool, utilizing Sentinel-1 or RISAT C-band radar backscatter which penetrates clouds completely."*

### Q4: "Where does the satellite imagery come from and does it cost money?"
> **Answer:** *"Our primary optical sensor data is 100% free and open-source from the European Space Agency's Copernicus Data Space Ecosystem (Sentinel-2 L2A BOA reflectance). We also support open data from USGS Landsat-8/9 and can ingest ISRO Cartosat and RISAT data through standard GeoTIFF/HDF5 formats."*
