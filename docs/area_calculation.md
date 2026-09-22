# SatQuery AI — Physical Area Calculation & Prevention of 0.0 ha Artifacts
**Smart India Hackathon 2026 | PS ID: 26167 (ISRO / Department of Space)**

---

## 1. Overview
The "0.0 ha" problem in remote sensing software occurs when:
1. Static default placeholder values (e.g. `0.0 ha`) are rendered in UI DOM templates before an analysis job finishes.
2. Area calculation pipelines assume a zero-valued scale factor or fail to convert geographic degrees ($^\circ$) to metric units ($m^2$).
3. Cloud-masked pixels or thresholding filters discard valid observations without fallback or notice.

SatQuery AI eliminates this problem through deterministic math in `backend/app/processing/area_stats.py` and strictly deferred UI card rendering.

---

## 2. Mathematical Formulation

### 2.1 Sentinel-2 Level-2A 10m Optical Grid
For calibrated Sentinel-2 MSI products (B02, B03, B04, B08):
- Pixel Ground Sample Distance: $10\text{ m} \times 10\text{ m} = 100\text{ m}^2$
- Since $1\text{ ha} = 10,000\text{ m}^2$:
  $$1\text{ pixel} = \frac{100\text{ m}^2}{10,000\text{ m}^2/\text{ha}} = 0.01\text{ ha}$$
- Total Area for $N_k$ classified pixels of class $k$:
  $$\text{Area}_k\ (\text{ha}) = N_k \times 0.01$$

### 2.2 Projected Coordinate Reference Systems (e.g. UTM)
Given an affine transform $[a, b, c, d, e, f]$:
$$\text{Pixel Area } (m^2) = |a \cdot e - b \cdot d|$$
$$\text{Pixel Area } (ha) = \frac{\text{Pixel Area } (m^2)}{10,000}$$

### 2.3 Geographic Coordinate Systems (WGS-84 / EPSG:4326)
Given pixel dimensions $\Delta \lambda$ (longitude degrees) and $\Delta \phi$ (latitude degrees) at scene center latitude $\phi$:
$$\Delta x\ (m) = \Delta \lambda \times 111,320 \times \cos(\phi)$$
$$\Delta y\ (m) = \Delta \phi \times 111,320$$
$$\text{Pixel Area } (m^2) = \Delta x \times \Delta y$$
$$\text{Pixel Area } (ha) = \frac{\text{Pixel Area } (m^2)}{10,000}$$

---

## 3. Semantic Change Classes & Area Breakdown

| Class ID | Semantic Transition | Color Code | Scientific Criteria |
| :---: | :--- | :---: | :--- |
| `1` | **New Built-up / Impervious** | 🔴 `#ef4444` | $\Delta \text{NDBI} > +0.12 \land \Delta \text{NDVI} < -0.10$ |
| `2` | **Vegetation Increase** | 🟢 `#22c55e` | $\Delta \text{NDVI} > +0.15 \land \text{NDVI}_{T2} \ge 0.30$ |
| `3` | **Vegetation Loss / Clearing** | 🟡 `#eab308` | $\Delta \text{NDVI} < -0.15 \land \text{NDVI}_{T1} \ge 0.30$ |
| `4` | **Water Surface Inundation** | 🔵 `#06b6d4` | $\Delta \text{NDWI} > +0.15 \land \text{NDWI}_{T2} \ge 0.10$ |
| `5` | **Water Body Recession** | 🟣 `#a855f7` | $\Delta \text{NDWI} < -0.15 \land \text{NDWI}_{T1} \ge 0.10$ |
| `255` | **Atmospheric / Cloud Mask** | ⚪ Hatched | Blue reflectance $B02 > 0.28 \lor \text{CloudProb} > 50\%$ |

---

## 4. UI Rendering Safeguards
- **Deferred Display**: The physical area statistics card `#cardPhysicalStats` has CSS class `hidden` on initial load. It is only revealed when `fetchAndRenderResults(jobId)` receives validated, non-null numeric metrics from `GET /api/analysis/{job_id}/results`.
- **Zero-Value Transparency**: If no change occurred in a category, the UI displays `0.00 ha (0 pixels)` rather than hiding the row or showing a misleading default.
