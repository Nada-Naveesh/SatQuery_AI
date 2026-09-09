# Real Satellite Data Strategy & Open Data Architecture (PS 26167)

**Problem Statement ID:** 26167  
**Title:** SatQuery AI — Multimodal Remote Sensing Operations Assistant  
**Theme:** Space Technology  
**Organization:** ISRO / Department of Space  

---

## 1. Two-Layer Data Architecture

SatQuery AI implements a robust, two-layer data operational model:

```
+-----------------------------------------------------------------------------------+
|                        SATQUERY AI DUAL-LAYER DATA STRATEGY                       |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  LAYER 1: PRELOADED REAL SATELLITE DEMO SCENARIOS (`data/demo_scenarios/`)        |
|  - Real satellite data chips in GeoTIFF format with spatial metadata.             |
|  - Instant 1-click execution for SIH jury evaluation (zero download wait time).   |
|  - Verified sensor parameters: Sentinel-2 L2A, LEVIR-CD, Cartosat-2S & SAR.       |
|                                                                                   |
|  LAYER 2: ARBITRARY USER UPLOAD FLOW                                              |
|  - Operators can upload custom single, temporal, or cross-modal satellite scenes. |
|  - Ingestion supports GeoTIFF/TIFF, PNG, and JPEG.                                |
|  - Spatial & band validator checks CRS, GSD resolution, and radiometric depth.    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Recommended Open Satellite Data Repositories

| Sensor / Constellation | Organization / Portal | Typical Revisit & Band Specs | Application in SatQuery AI |
| :--- | :--- | :--- | :--- |
| **Sentinel-2A/B (MSI)** | European Space Agency (ESA) Copernicus | 5-day revisit; 13 spectral bands (10m, 20m, 60m VNIR/SWIR) | **Scenario 1 (Flood VQA & Grounding)**: Chlorophyll absorption, water delineation (NDWI), and flood perimeter mapping. |
| **Sentinel-1A/C (C-SAR)** | ESA / Alaska Satellite Facility (ASF) | 6-day repeat; C-Band (5.405 GHz) dual-pol (VV, VH) | **Scenario 3 (Optical-SAR Fusion)**: All-weather day/night cloud penetration, radar cross-section backscatter ($\sigma^0_{\text{dB}}$). |
| **Cartosat-2S / Cartosat-3** | ISRO Space Applications Centre (SAC) | High-Resolution Panchromatic & Multispectral (0.28m–0.65m) | **Scenario 3 / ISRO Hidden Set**: High-detail urban infrastructure mapping and port asset recognition. |
| **LEVIR-CD Benchmark** | Beihang University / IEEE GRSS | Multi-temporal paired optical scenes (0.5m GSD) | **Scenario 2 (Bi-Temporal Change)**: Urban expansion, deforestation, and road construction tracking. |
| **BigEarthNet.txt Archive** | TU Berlin & ESA | 590k paired Sentinel-1 SAR + Sentinel-2 multispectral patches | **Domain Adaptation**: Core multimodal instruction tuning and feature alignment for the specialist model registry. |

---

## 3. How Demo Chips Were Prepared

1. **Spatial Sub-setting (Cropping):**
   - Full Sentinel-2 tiles ($10,000 \times 10,000$ pixels, $\sim 500$ MB) were cropped to standard $512 \times 512$ chips focused on critical regions of interest (e.g. river basins, industrial corridors, ports).
2. **Radiometric Calibration:**
   - Optical: Level-2A bottom-of-atmosphere (BOA) surface reflectance normalized with dynamic percentile stretching ($2\% - 98\%$).
   - SAR: Calibrated $\sigma^0$ radar backscatter converted to decibels:
     $$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\text{intensity}^2)$$
3. **Co-Registration:**
   - Cross-modal pairs (Optical and SAR) were reprojected to a common spatial grid (`EPSG:4326` / WGS 84) using bilinear interpolation to assure pixel-level correspondence.
4. **GeoTIFF Formatting:**
   - Exported as standard uncompressed TIFF/GeoTIFF with embedded spatial metadata.

---

## 4. Re-running the Automated Data Setup

To initialize or verify all demonstration scenarios on any machine:

```bash
python scripts/download_demo_data.py
```

This guarantees that judges, reviewers, and teammates will always have fully operational real satellite imagery ready out-of-the-box.
