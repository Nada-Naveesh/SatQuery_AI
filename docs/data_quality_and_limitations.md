# Data Quality Assessment & System Limitations

**Smart India Hackathon 2026 | Problem Statement ID: 26167**  
**Theme:** Space Technology | **ISRO / SAC**

---

## 1. Rationale: Eliminating Arbitrary Confidence Scoring

A common pitfall in AI hackathon projects is displaying hardcoded confidence numbers (such as an unvarying "93%") regardless of cloud cover, sensor noise, or alignment. In professional aerospace and defense applications (e.g., ISRO SAC, National Remote Sensing Centre), arbitrary confidence scores represent a critical vulnerability.

SatQuery AI introduces a **dynamically calculated, auditable Quality & Confidence Engine** ([`backend/app/processing/statistics.py`](file:///c:/Users/Nada%20Naveesh/OneDrive/Desktop/Satquery-AI/backend/app/processing/statistics.py)). Every score returned by the platform is mathematically derived from physical atmospheric and geometric indicators.

---

## 2. Dynamic Confidence Mathematical Formulation

The confidence score $C \in [0.0, 1.0]$ is computed as a weighted sum of five orthogonal remote-sensing quality metrics:

$$
C = 0.25 \, Q_{\text{valid}} + 0.20 \, Q_{\text{cloud}} + 0.20 \, Q_{\text{overlap}} + 0.20 \, Q_{\text{reg}} + 0.15 \, Q_{\text{signal}}
$$

| Term | Metric Name | Weight | Physical Definition |
| :--- | :--- | :--- | :--- |
| $Q_{\text{valid}}$ | **Valid Data Ratio** | 0.25 | Proportion of non-zero, valid digital number pixels across both acquisition rasters: $\frac{\sum(M_{\text{data}}^{T1} \land M_{\text{data}}^{T2})}{N_{\text{total}}}$ |
| $Q_{\text{cloud}}$ | **Clear Atmospheric Ratio** | 0.20 | Complement of joint optical cloud and shadow contamination: $1.0 - \text{CloudFrac}_{\text{joint}}$ |
| $Q_{\text{overlap}}$ | **Spatial Overlap Ratio** | 0.20 | Geometric Intersection-over-Union (IoU) of the $T_1$ and $T_2$ spatial coverage footprints |
| $Q_{\text{reg}}$ | **Registration Quality** | 0.20 | Sub-pixel spatial alignment score derived from phase correlation across spatial gradient edges ($1.0$ for identical grids) |
| $Q_{\text{signal}}$ | **Spectral Signal Quality** | 0.15 | Measurement of dynamic range and contrast across NIR and red bands, penalizing sensor saturation and low-radiance fog |

### Confidence Classification Tiers

| Calculated Score ($C$) | UI & PDF Badge | Operational Meaning |
| :--- | :--- | :--- |
| **$C \ge 0.85$** | **High Confidence** (Green) | Cloud-free optical observation with optimal atmospheric transmission and verified sub-pixel registration. Results are actionable for official planning. |
| **$0.70 \le C < 0.85$** | **Moderate Confidence** (Amber) | Valid spectral signatures with minor seasonal illumination differences, light haze, or partial boundary cropping. Results should be cross-verified. |
| **$C < 0.70$** | **Low / Caution** (Red) | High cloud contamination, severe shadow distortion, or marginal overlap. Analysis is advisory only; SAR radar fusion recommended. |

---

## 3. Real-Time Telemetry & Trace Auditability

Every inference response includes full quality telemetry:
```json
{
  "quality_score": 0.94,
  "quality_assessment": {
    "valid_pixel_percentage": 100.0,
    "cloud_pixel_percentage": 0.0,
    "overlap_ratio": 1.0,
    "spatial_registration": "sub-pixel aligned (good)",
    "overall_quality": 0.94,
    "confidence_calibration": "High confidence (optimal optical observation)"
  }
}
```

In the user interface, judges can click **Quality View** to examine the atmospheric mask and validity layer directly on the canvas.

---

## 4. Known Physical Limitations of Optical Satellite Data

Transparency regarding physical constraints demonstrates mature engineering judgment:

### 1. Cloud Penetration Ceiling in Optical Bands
- **Limitation**: Optical sensors (Sentinel-2, Cartosat, Landsat) cannot penetrate dense monsoon cloud layers or smoke plumes.
- **SatQuery AI Solution**: When thick cloud cover is detected ($Q_{\text{cloud}} < 0.60$), the Agentic Router triggers the **Optical + SAR Fusion Tool** ([`fusion_tool.py`](file:///c:/Users/Nada%20Naveesh/OneDrive/Desktop/Satquery-AI/backend/app/tools/fusion_tool.py)), fusing microwave C-band Synthetic Aperture Radar (Sentinel-1 / RISAT-1) to penetrate the cloud cover.

### 2. Spatial Resolution Limitations ($10\,\text{m}$ GSD)
- **Limitation**: At $10\,\text{m}$ Ground Sampling Distance, an individual pixel represents $100\,\text{m}^2$. It is impossible to resolve individual automobiles, narrow utility cables, or person-level details.
- **SatQuery AI Solution**: The system focuses on meso-scale changes: buildings, road networks, water bodies, agricultural parcels, and port docks. The Minimum Mapping Unit (MMU=9 px, $900\,\text{m}^2$) strictly filters out sub-pixel false positives.

### 3. Phenological & Seasonal False Alarms
- **Limitation**: Normal agricultural crop cycles (monsoon greening vs. post-harvest dry fallow) produce strong $\Delta\text{NDVI}$ signals that are not true land-use changes.
- **SatQuery AI Solution**: Built-up infrastructure detection requires simultaneous positive built-up index ($\Delta\text{NDBI} > +0.20$) coupled with permanent vegetation decline, preventing harvested fields from being mistaken for concrete buildings.

### 4. Coastal Sun Glint & Turbidity
- **Limitation**: Shallow tidal sandbanks and high suspended sediment in river deltas (e.g., Avanigadda, Godavari mouth) can alter water reflectance spectra.
- **SatQuery AI Solution**: High-threshold water index checks ($\text{NDWI} > 0.0$ and $\Delta\text{NDWI} > +0.25$) are used to isolate genuine water expansion and flood submergence.
