# SatQuery AI — Complete User Manual & Judge Demo Guide

**Smart India Hackathon 2026 | Problem Statement ID: 26167**  
**Theme:** Space Technology  
**Organization:** Indian Space Research Organisation (ISRO) / Space Applications Centre (SAC)  

---

## 1. What is SatQuery AI?

**SatQuery AI** is an interactive vision-language assistant that allows anyone—from emergency response coordinators and municipal officers to hackathon judges—to analyze satellite imagery using **everyday conversational English**.

Usually, understanding satellite data requires deep technical training: writing Python GIS scripts, calibrating 12 spectral bands, converting radar backscatter, and calculating difference matrices. 

With SatQuery AI:
- You simply **select a location or upload satellite photos**.
- Ask a question in **plain English** (e.g., *"What changed here between 2025 and 2026?"* or *"Where are the buildings?"*).
- SatQuery AI's **Agentic Router** analyzes the images, highlights features on the map, provides a simple explanation, and generates a **downloadable PDF report** in seconds.

---

## 2. Quickstart (How to Run in 1 Minute)

### Step 1: Start the Application Server
Open PowerShell or your command terminal in the project directory (`Satquery-AI`) and run:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Open Mission Control in Your Web Browser
Open your browser to:
🌐 **`http://localhost:8000`**

The single-page **Mission Control Dashboard** will load with full state-wide satellite coverage, interactive map viewer, and pre-configured scenarios.

---

## 3. Exploring Andhra Pradesh State-Wide Coverage

SatQuery AI includes authentic bi-temporal (2025 vs. 2026) Sentinel-2 satellite imagery covering all major regions of **Andhra Pradesh**:

| Region / City | Coordinates | Focus Area & Key Features |
| :--- | :--- | :--- |
| **Vijayawada** | 16.51°N, 80.65°E | Krishna River corridor, Prakasam Barrage, bypass expressway, urban expansion |
| **Amaravati** | 16.54°N, 80.51°E | AP Capital Region, Secretariat complex, Seed Access road construction |
| **Visakhapatnam** | 17.69°N, 83.22°E | Deepwater port, breakwater jetty extension, coastal container yards |
| **Tirupati** | 13.63°N, 79.42°E | Seshachalam foothills, transit infrastructure, temple town expansion |
| **Guntur** | 16.31°N, 80.44°E | Agricultural trading hub, outer ring logistics, farmland conversion |
| **Rajahmundry** | 17.00°N, 81.80°E | Godavari River basin, Dowleswaram barrage embankments, river transport |
| **Kakinada** | 16.99°N, 82.25°E | Deepwater port, Coringa mangrove wetland health, coastal development |
| **Kurnool** | 15.83°N, 78.04°E | Tungabhadra river basin, Ultra Mega Solar Park photovoltaic arrays |
| **Nellore** | 14.44°N, 79.99°E | Pennar river delta, intensive coastal aquaculture water ponds |
| **Anantapur** | 14.68°N, 77.60°E | Semi-arid drought monitoring, renewable wind/solar farms, water harvesting |
| **Gudlavalleru** | 16.02°N, 80.70°E | Krishna delta agricultural grid, engineering campus corridor |
| **Entire AP State** | 15.91°N, 79.74°E | Macro regional mosaic across Eastern Ghats and Bay of Bengal coastline |

### How to Switch Between Cities
1. **Quick City Buttons:** Click any of the teal city pills at the top of the left panel (e.g. *Vijayawada*, *Amaravati*, *Visakhapatnam*, *Kurnool*).
2. **Search Bar:** Type any city or place name into the search box and click **Locate** (or press `Enter`).
3. Notice that the coordinates (`AOI: Lat, Lon`) update dynamically and the 2025 vs. 2026 satellite image pair is instantly loaded into the viewport.

---

## 4. How to Ask Questions & Run Analyses

### Example 1: Comparing 2025 vs. 2026 (Change Detection)
1. Click the **Vijayawada** or **Amaravati** pill.
2. Select the suggestion pill: **🔄 What changed here?**  
   *(Or type: `"What changed between 2025 and 2026 in this area?"`)*
3. Click **Analyze Satellite Images**.
4. **Result:**
   - The direct answer explains where new roads, buildings, or water bodies appeared.
   - Colored highlights appear on the map showing exact areas of new construction.
   - You can toggle the **Split Comparison** slider to wipe between the before (2025) and after (2026) views.

### Example 2: Finding Buildings & Urban Structures (Object Grounding)
1. In the query box, type:
   `"Where are the buildings in this image?"`
2. Click **Analyze Satellite Images**.
3. **Result:**
   - SatQuery AI identifies built-up areas and draws colored boundary boxes around commercial and residential structures.

### Example 3: Finding Water Bodies & Flood Extent (Water Mapping)
1. Click the **💧 Show water bodies** suggestion button.  
   *(Or type: `"Show me the water bodies."` or `"Identify submerged agricultural parcels."`)*
2. Click **Analyze Satellite Images**.
3. **Result:**
   - SatQuery AI highlights all ponds, rivers, canals, and flooded fields in azure blue and reports the total surface area in hectares.

### Example 4: Piercing Monsoon Clouds with Radar (Optical + SAR Fusion)
1. Click **3. Optical-SAR Cloud Penetration** in the left scenario list.
2. Click **Analyze Satellite Images**.
3. **Result:**
   - Demonstrates all-weather capability: while the optical photo is completely covered by thick white clouds, the radar signals pierce through the haze to reveal oil storage tanks, harbor piers, and coastline.

---

## 5. Understanding the Visual Viewport Controls & 4 View Modes

In the right-hand panel, you can control how satellite evidence is displayed:

- **4 View Modes:**
  - **Base (T2):** Displays the post-change acquisition satellite scene without overlays.
  - **Evidence Overlay:** Overlays the physical calculated change mask on top of the satellite image.
  - **Split Comparison:** Activates an interactive swipe wiper. Drag the central red handle left or right across the canvas to compare before (T1) and after (T2) views in real time.
  - **Quality View:** Visualizes the joint atmospheric cloud mask and data validity layer, reporting clear optical transmission percentage and registration quality.
- **Layer Opacity Slider (10% - 100%):** Dynamically adjusts overlay transparency so underlying ground features remain clearly visible beneath the evidence layer.
- **Calculated Change Legend:**
  - 🔴 **Red (`#EF4444`):** New Built-up & Paved Infrastructure ($\Delta\text{NDBI} > +0.20 \land \Delta\text{NDVI} < -0.10$)
  - 🟢 **Green (`#22C55E`):** Vegetation Growth / Canopy Expansion ($\Delta\text{NDVI} > +0.20$)
  - 🟡 **Yellow (`#EAB308`):** Vegetation Loss / Land Clearing ($\Delta\text{NDVI} < -0.20$)
  - 🔵 **Cyan (`#06B6D4`):** Water Inundation / Flood Expansion ($\Delta\text{NDWI} > +0.25$)
  - 🟣 **Purple (`#A855F7`):** Water Body Decline / Drying ($\Delta\text{NDWI} < -0.25$)
- **Ground-Truth Physical Area Breakdown Card:**
  - Displays dynamic hectare statistics calculated directly from pixel counts at $10\text{m}$ GSD ($1\text{ px} = 0.01\text{ ha}$).
  - Shows Total Changed Hectares, Percentage of AOI, New Built-up ha, Vegetation Loss ha, and Water Changes ha.
- **Tactical Coordinates HUD:**
  - Real-time overlay in the top-left of the viewport displaying location name, latitude/longitude, and WGS84 bounding box.

---

## 6. How to Upload Your Own Satellite Images

1. Download satellite imagery (GeoTIFF, PNG, or JPG) from [Copernicus Browser](https://browser.dataspace.copernicus.eu) or USGS EarthExplorer (see [How to Get Free Satellite Data](file:///docs/how_to_get_data.md)).
2. Click the **Upload Satellite Images** box on the left panel (or drag and drop your file).
   - For single image analysis: upload 1 image.
   - For before-and-after change detection: select both the 2025 and 2026 images simultaneously.
3. Type your question in plain English.
4. Click **Analyze Satellite Images**.

---

## 7. Downloading the Executive PDF Report

After running any analysis, you can download an official mission report:

1. Click the **PDF Report** button in the top navigation bar.
2. The system generates a clean, executive PDF report (`SatQuery_MissionReport_<ID>.pdf`).
3. **What is inside the report:**
   - **Main Findings:** Plain English summary of what was detected, suitable for non-technical officials or judges.
   - **Calculated Evidence Overlay:** The exact same colorized change mask rendered in the browser viewport.
   - **Ground-Truth Hectare Statistics Table:** Full breakdown of new built-up area, vegetation changes, and water coverage in hectares.
   - **Confidence Score & Audit ID:** Uniquely verifiable trace ID confirming that results are grounded in real satellite telemetry.
   - **Technical Notes:** Sensor type, resolution (10m GSD), geographic coordinates, CRS (EPSG:4326), and execution latency.

---

## 8. SIH 2026 Evaluation Checklist for Judges

| Evaluation Criteria | How SatQuery AI Fulfills It | Verified In |
| :--- | :--- | :--- |
| **Evidence-Based Raster Overlays** | Every colored pixel is derived from physical multi-band calculations ($\text{NDVI}, \text{NDWI}, \text{NDBI}$ + MMU=9), not synthetic graphics. | `backend/app/processing/` & Viewport |
| **Dynamic Hectare Area Quantification** | True physical area calculated at $10\text{m}$ GSD ($0.01\,\text{ha}/\text{px}$) with zero static placeholders. | Hectare Stats Card & PDF Report |
| **Honest Quality-Aware Confidence** | Mathematically calibrated from atmospheric valid pixels, cloud cover, and spatial registration (never hardcoded 93%). | `statistics.py` & Quality View |
| **4 Interactive View Modes** | Base, Evidence Overlay, Draggable Split Comparison Slider, and Atmospheric Quality View. | Satellite Viewport Controls |
| **3 Verified Competition Packages** | Gudlavalleru (+242.1 ha built-up), Machilipatnam (+158.3 ha port), and Godavari (+627.5 ha flood). | Featured Scenarios & `backend/demo_data/` |
| **Live Place Search & Copernicus Ingestion** | OpenStreetMap Nominatim geocoding paired with live Copernicus CDSE Sentinel-2 STAC search. | Location Search & Copernicus Tab |
| **Auditable Execution Trace & Telemetry** | Full trace with router reasoning, tool execution latency, and downloadable machine-readable JSON. | Trace Accordion & Trace Modal |
| **Executive Defense-Grade PDF Reporting** | Print-ready PDF report matching the exact browser overlay, hectare numbers, and metadata. | `/api/v1/report/pdf` |
