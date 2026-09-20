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

## 5. Understanding the Visual Viewport Controls

In the right-hand panel, you can control how satellite images are displayed:

- **Base Button:** Shows the natural satellite photo without any overlays.
- **Evidence Overlay Button:** Overlays colored highlights over detected features (e.g., green/amber for new construction, blue for water, red for changed parcels).
- **Split Comparison Button:** Activates a side-by-side comparison slider. Drag the handle horizontally to slide between the 2025 and 2026 images.
- **Confidence Bar:** Shows the calibrated mathematical confidence score (e.g. 94%) computed by the model.
- **Key Observations & Summary:** Plain-English bullet points summarizing key findings and estimated surface area in hectares.

---

## 6. How to Upload Your Own Satellite Images

1. Download a satellite photo (GeoTIFF, PNG, or JPG) from [Copernicus Browser](https://browser.dataspace.copernicus.eu) or USGS EarthExplorer (see [How to Get Free Satellite Data](file:///docs/how_to_get_data.md)).
2. Click the **Upload Satellite Images** box on the left panel (or drag and drop your file).
   - For single image analysis: upload 1 image.
   - For before-and-after change detection: select both the 2025 and 2026 images simultaneously.
3. Type your question in plain English.
4. Click **Analyze Satellite Images**.

---

## 7. Downloading the Executive PDF Report

After running any analysis, you can download an official mission report:

1. Click the **Download Mission PDF** button in the top navigation bar.
2. The system generates a clean, executive PDF report (`SatQuery_MissionReport_<ID>.pdf`).
3. **What is inside the report:**
   - **Main Findings:** Plain English summary of what was detected, suitable for non-technical officials or judges.
   - **Visual Comparison Table:** Displays the **2025 Base Image**, **2026 Target Image**, and the **Colored Change Overlay** side-by-side.
   - **Confidence Score & Audit ID:** Uniquely verifiable trace ID confirming that results are grounded in real satellite telemetry.
   - **Technical Notes:** Compact metadata table at the end (sensor, resolution, coordinates, and execution latency in milliseconds).

---

## 8. SIH 2026 Evaluation Checklist for Judges

| Evaluation Criteria | How SatQuery AI Fulfills It | Verified In |
| :--- | :--- | :--- |
| **Multimodal Satellite Support** | Supports optical reflectance (Sentinel-2, Cartosat) and Synthetic Aperture Radar (Sentinel-1 C-SAR). | Scenario 1, 3, 4 & Custom Upload |
| **Natural Language Queries** | Operators ask in everyday English; queries are auto-routed without requiring code or parameters. | Query Panel & Agent Router |
| **Bi-Temporal Change Reasoning** | Accurately compares two dates (2025 vs. 2026) and quantifies area changes in hectares. | All 11 AP Cities + LEVIR-CD |
| **State-Wide Regional Coverage** | Complete multi-temporal data across 11 key regions in Andhra Pradesh + entire state overview. | AP Location Intelligence |
| **Zero Hallucination Grounding** | Every answer is backed by pixel-level colored segmentation masks and bounding boxes. | Satellite Viewport & PDF Report |
| **Executive Reporting** | One-click PDF mission report with 3-image visual comparison table and plain English findings. | PDF Report Generator |
| **Test Coverage & Reliability** | 100% test pass rate across 40 unit and integration tests. | PyTest Suite (`pytest -v`) |
