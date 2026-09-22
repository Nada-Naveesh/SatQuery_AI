# SatQuery AI — Satellite Image Upload Workflow
**Smart India Hackathon 2026 | PS ID: 26167 (ISRO / Department of Space)**

---

## 1. Overview
Operators can upload arbitrary pairs of satellite imagery ($T_1$ Before and $T_2$ After) for sub-pixel change detection, multi-index classification, and spatial statistics.

SatQuery AI supports both **Georeferenced Rasters (GeoTIFF)** and **Standard Images (PNG/JPEG)** with transparent, honest scale reporting.

---

## 2. Supported Image Formats

| Format | Extension | Spatial Metadata | Area Measurement Mode |
| :--- | :--- | :--- | :--- |
| **GeoTIFF** | `.tif`, `.tiff` | CRS (e.g. UTM, EPSG:4326), Affine Transform ($6\times$ coefficients) | Certified physical hectares ($ha$) calculated from exact raster transform matrix |
| **Standard RGB** | `.png`, `.jpg`, `.jpeg` | None (Pixel raster dimensions only) | Pixel counts + Estimated scale based on assumed 10m GSD with prominent disclaimer |

---

## 3. Scale Integrity & Preventing Fabricated Metrics
In remote sensing systems, reporting made-up surface areas for non-georeferenced images is a critical error. SatQuery AI handles this with strict mathematical integrity:
1. **GeoTIFF Ingestion**:
   - The affine transform matrix is extracted:
     $$\text{Transform} = [a, b, c, d, e, f]$$
   - In projected CRS (e.g., UTM Zone 44N):
     $$\text{Pixel Area } (m^2) = |a \cdot e - b \cdot d|$$
     $$\text{Area } (ha) = \frac{\text{Pixel Area } (m^2)}{10,000}$$
   - In geographic CRS (WGS-84 / EPSG:4326):
     $$\text{Geodesic Area } (m^2) = (\Delta \lambda \cdot 111,320 \cdot \cos \phi) \cdot (\Delta \phi \cdot 111,320)$$
2. **Standard PNG/JPEG Ingestion**:
   - The system flags `is_georeferenced = False`.
   - Physical hectare numbers are omitted from official metrics to prevent false precision.
   - An explanatory notice is surfaced in the UI and PDF:
     > *"Notice: Physical area in hectares is unavailable because this uploaded file does not contain geographic coordinate scale metadata. Delineation is reported in exact classified pixel counts."*

---

## 4. Co-Registration & Alignment
When two rasters of slightly differing dimensions or alignments are uploaded:
1. Both scenes are resampled to a common coordinate frame and uniform dimensions ($H \times W$).
2. Sub-pixel phase cross-correlation or feature matching evaluates mutual registration.
3. Registration quality ($Q_{reg}$) is scored and integrated into the final confidence assessment.
