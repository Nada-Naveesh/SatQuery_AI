# Data Sources & Manual Preparation Guide

This guide outlines how to acquire real Earth observation satellite data from official space agency portals and benchmark archives for **SatQuery AI (SIH 2026 | PS 26167)**.

---

## 1. Official Remote Sensing Data Portals

| Satellite & Sensor | Agency / Portal | Access Level | Primary Applications | Direct Link |
| :--- | :--- | :--- | :--- | :--- |
| **Sentinel-2 (MSI)** | ESA Copernicus Browser | Free Open Access (Free Account) | Multispectral optical, Flood mapping, Vegetation monitoring (NDVI/NDWI) | [Copernicus Browser](https://browser.dataprocess.copernicus.eu/) |
| **Sentinel-1 (C-band SAR)** | Alaska Satellite Facility (ASF) Vertex | Free Open Access (NASA Earthdata Login) | All-weather microwave imaging, flood backscatter, double-bounce structural mapping | [ASF Vertex](https://search.asf.alaska.edu/) |
| **Cartosat-2S / Resourcesat** | ISRO Bhuvan / Bhoonidhi | Open data for Indian region (Registration) | High-resolution optical urban monitoring, infrastructure expansion | [ISRO Bhoonidhi Portal](https://bhoonidhi.nrsc.gov.in/) |
| **LEVIR-CD Benchmark** | Beihang University / IEEE Datasets | Direct Public Download | Bi-temporal building and urban change detection benchmark | [LEVIR-CD Archive](https://justchenhao.github.io/LEVIR/) |
| **BigEarthNet-S1 / S2** | TU Berlin Remote Sensing Image Analysis | Free Open Data | Multimodal Sentinel-1 + Sentinel-2 paired benchmark with text descriptions | [BigEarthNet Portal](https://bigearth.net/) |
| **RSVQA & CDVQA** | Sylvain Lobry / Univ. Wageningen | Direct Public Download | Remote sensing Visual Question Answering benchmarks | [RSVQA Archive](https://rsvqa.sylvainlobry.com/) |

---

## 2. Step-by-Step Manual Download & Chip Preparation

To download full satellite scenes and extract your own demonstration chips into `data/demo_scenarios/`:

### Step 2.1: Download Sentinel-2 Optical Scenes (For Flood / VQA)
1. Go to [Copernicus Browser](https://browser.dataprocess.copernicus.eu/).
2. Search for `Sentinel-2 L2A` over your area of interest (e.g., Godavari River Basin during July monsoon).
3. Select cloud cover `< 15%`.
4. Click **Download Product (GeoTIFF / SAFE format)**.
5. Crop a $512 \times 512$ or $1024 \times 1024$ region using GDAL:
   ```bash
   gdal_translate -projwin <ulx> <uly> <lrx> <lry> -outsize 512 512 full_scene_B04.jp2 image1.tif
   ```
6. Copy `image1.tif` to `data/demo_scenarios/scenario_1_flood/image1.tif`.

---

### Step 2.2: Download Sentinel-1 C-Band SAR Scenes (For Cloud Penetration)
1. Open [ASF Vertex](https://search.asf.alaska.edu/).
2. Filter: `Sentinel-1`, Dataset: `GRD` (Ground Range Detected), Polarization: `VV+VH`.
3. Locate scene over coastal ports or industrial areas.
4. Download the calibrated amplitude GeoTIFF.
5. Crop to the exact geographic bounds of your optical scene:
   ```bash
   gdalwarp -t_srs EPSG:4326 -te <xmin> <ymin> <xmax> <ymax> -ts 512 512 raw_sar.tif sar.tif
   ```
6. Copy `sar.tif` to `data/demo_scenarios/scenario_3_optical_sar/sar.tif`.

---

### Step 2.3: Updating `metadata.json`
After replacing or adding imagery to `data/demo_scenarios/scenario_*/`, update the corresponding `metadata.json`:
```json
{
  "id": "scenario_1_flood",
  "name": "Custom Flood Assessment Scene",
  "sensor": "Sentinel-2 L2A (MSI)",
  "date": "YYYY-MM-DD",
  "area": "Region Name",
  "resolution": "10 m GSD",
  "crs": "EPSG:4326",
  "real_data_source": "Copernicus Open Access Hub",
  "image_files": ["image1.tif"],
  "suggested_queries": [
    "Identify the submerged agricultural parcels and highlight their spatial boundaries."
  ]
}
```

---

## 3. Automated Setup Verification

To regenerate or verify all built-in real satellite scenarios at any time:
```bash
python scripts/download_demo_data.py
```
