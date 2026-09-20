# Where & How to Get Free Satellite Imagery for SatQuery AI

**SatQuery AI** supports standard Earth Observation satellite data from all major space agencies. You can either use the pre-loaded demonstration scenes (such as Andhra Pradesh cities, Godavari flood, or LEVIR-CD) or download authentic satellite images for **any location in the world** and upload them directly into the system.

This guide provides a step-by-step tutorial on where to find free satellite data, how to download it, and how to analyze it in SatQuery AI.

---

## 1. Official Free Satellite Data Portals

| Portal | Space Agency | Resolution | Imagery Types | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **[Copernicus Browser](https://browser.dataspace.copernicus.eu)** | ESA (Europe) | **10 meters** | Sentinel-2 (Optical, 13 bands)<br>Sentinel-1 (Radar SAR) | **Recommended for SatQuery AI**<br>5-day global updates, free GeoTIFF & PNG downloads. |
| **[USGS EarthExplorer](https://earthexplorer.usgs.gov)** | USGS / NASA (USA) | **30 meters** | Landsat 8 & Landsat 9 (Optical & Thermal) | Long-term historical change detection (archive goes back to 1972). |
| **[ISRO Bhuvan / Bhoovikram](https://bhuvan.nrsc.gov.in)** | ISRO / NRSC (India) | **Various** | Resourcesat (LISS-3/4), Cartosat DEM | Indian territory geospatial layers and open satellite products. |
| **[NASA Earthdata](https://search.earthdata.nasa.gov)** | NASA (USA) | **250m – 1km** | MODIS, VIIRS | Large-scale regional wildfire, flood, and climate monitoring. |

---

## 2. Step-by-Step Tutorial: Downloading from Copernicus Browser

The **Copernicus Data Space Browser** is the easiest, fastest, and most modern portal to download free Sentinel-2 imagery.

### Step 1: Open the Browser
Visit the official portal in your web browser:
🔗 **[https://browser.dataspace.copernicus.eu](https://browser.dataspace.copernicus.eu)**

*(Optional: Create a free account to enable direct GeoTIFF analytical downloads; high-resolution PNGs can be downloaded immediately).*

### Step 2: Search Your Region of Interest (AOI)
- Use the search bar in the top-left to enter any place name (e.g., *Vijayawada*, *Gudlavalleru*, *Amaravati*, *Visakhapatnam*, or any international city).
- Zoom in until you see roads, rivers, water bodies, and farmland clearly.

### Step 3: Select Satellite Sensor & Cloud Cover Filter
- In the left sidebar under **Visualization** or **Search**:
  - Select **Sentinel-2**.
  - Choose **Sentinel-2 L2A** (Level-2A Bottom-of-Atmosphere Reflectance — this gives natural surface colors without atmospheric haze).
  - Set **Max cloud coverage** to under **20%** (for clear surface visibility).
  - Pick your desired acquisition date:
    - For **Current state / Single analysis**: Choose the most recent clear date.
    - For **Change detection**: Pick one date from **2025** and one date from **2026** (e.g. August 2025 vs. August 2026).

### Step 4: Choose the Layer
- Click on **True Color** (Bands 4, 3, 2) — this displays the Earth exactly as the human eye sees it from space.
- Alternatively, select **False Color (Urban)** or **NDWI (Water index)** to highlight specific features.

### Step 5: Download the Satellite Image
1. In the right-hand vertical toolbar, click the **Download image** icon (camera/download button).
2. Choose your download format:
   - **Basic Tab (Easiest):**
     - Image format: **PNG** or **JPG**
     - Resolution: **High** (e.g. 2048 x 2048 or 1024 x 1024)
     - Show captions / scale bar: *Optional*
     - Click **Download**.
   - **Analytical Tab (For Full Geospatial Precision):**
     - Image format: **TIFF (8-bit or 16-bit)** or **GeoTIFF**
     - Coordinate Reference System (CRS): **WGS 84 (EPSG:4326)** or UTM
     - Layers: True Color RGB or Raw Spectral Bands (B02, B03, B04, B08)
     - Click **Download**.

---

## 3. How to Upload into SatQuery AI

Once you have downloaded your satellite image(s):

### Single-Image Analysis (Object Search, Flood, Land Use)
1. Open SatQuery AI at `http://localhost:8000`.
2. In the **Upload Satellite Images** box on the left, click to select your downloaded image (or drag and drop it).
3. Type your question in simple English:
   - *"Where are the buildings in this image?"*
   - *"Show me the water bodies."*
   - *"Identify the submerged agricultural parcels and highlight their spatial boundaries."*
4. Click **Analyze Satellite Images**.
5. View the direct answer, confidence score, and toggle **Evidence Overlay** to see the colored highlights over the image.

### Bi-Temporal Change Detection (2025 vs. 2026)
1. In the upload file dialog, **select two files simultaneously** (Hold `Ctrl` and select both images):
   - First image: Acquisition from 2025 (Before)
   - Second image: Acquisition from 2026 (After)
2. Type a change detection question in simple English:
   - *"What changed here between 2025 and 2026?"*
   - *"Has the built-up area increased?"*
   - *"Detect newly constructed roads, buildings, or water bodies."*
3. Click **Analyze Satellite Images**.
4. The system automatically computes the difference, highlights new construction or water loss in color, and displays an interactive **Split Comparison slider**.

---

## 4. Downloading the Executive PDF Report

After executing any analysis:
1. Click the **Download Mission PDF** button in the top navigation bar.
2. A publication-grade PDF report (`SatQuery_MissionReport_<ID>.pdf`) will open immediately.
3. The report is written in clear, simple English and includes:
   - Clear summary of findings (without heavy remote sensing jargon).
   - Side-by-side visual comparison table (2025 image, 2026 image, and colored change overlay).
   - Confidence score and audit verification ID.
