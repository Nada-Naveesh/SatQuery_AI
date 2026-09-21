# Scientific Methodology: Bi-Temporal Remote Sensing Change Detection

**Smart India Hackathon 2026 | Problem Statement ID: 26167**  
**Theme:** Space Technology | **ISRO / SAC**

---

## 1. Introduction

Automated bi-temporal change detection in satellite remote sensing involves comparing two coregistered Earth observation scenes acquired over the same geographic area at distinct times ($T_1$ and $T_2$) to detect, classify, and quantify land-use and land-cover (LULC) transformations.

SatQuery AI pairs **spectral difference analysis** ($\Delta\text{Index}$) with **morphological spatial filtering** (Minimum Mapping Unit) and **rule-based physical decision logic**. This methodology provides deterministic explainability, high computational throughput, and rigorous scientific auditability—qualities essential for defense and civil governance applications.

---

## 2. Mathematical Formulation of Spectral Indices

### Normalized Difference Vegetation Index (NDVI)
$$
\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}} + \epsilon}
$$
- **Spectral Rationale**: Healthy vegetation absorbs red light ($665\,\text{nm}$) for photosynthesis while strongly scattering near-infrared ($842\,\text{nm}$) via the spongy mesophyll structure of plant leaves.
- **Dynamic Range**: $[-1.0, +1.0]$. Dense canopy $> 0.60$; sparse vegetation $0.20 - 0.50$; bare soil $0.05 - 0.15$; water $< 0.0$.

### Normalized Difference Water Index (NDWI)
$$
\text{NDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{NIR}}}{\rho_{\text{Green}} + \rho_{\text{NIR}} + \epsilon}
$$
- **Spectral Rationale**: Water bodies exhibit higher reflectance in green wavelengths ($560\,\text{nm}$) and virtually zero reflectance in near-infrared ($842\,\text{nm}$) due to strong specular absorption.
- **Dynamic Range**: Water pixels satisfy $\text{NDWI} > 0.0$. Non-water terrestrial surfaces exhibit negative NDWI values.

### Normalized Difference Built-up Index (NDBI)
$$
\text{NDBI} = \frac{\rho_{\text{SWIR}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR}} + \rho_{\text{NIR}} + \epsilon} \approx \frac{\rho_{\text{Red}} - \rho_{\text{NIR}}}{\rho_{\text{Red}} + \rho_{\text{NIR}} + \epsilon}
$$
- **Spectral Rationale**: Artificial materials (concrete, asphalt, brick, corrugated metal) show pronounced reflectance in red/SWIR compared to NIR.
- **Dynamic Range**: Built-up structures and paved roads typically exhibit positive NDBI values, in sharp contrast to surrounding vegetation.

---

## 3. Decision Logic & Classification Hierarchy

Let $\Delta\text{NDVI} = \text{NDVI}_{T2} - \text{NDVI}_{T1}$, $\Delta\text{NDWI} = \text{NDWI}_{T2} - \text{NDWI}_{T1}$, and $\Delta\text{NDBI} = \text{NDBI}_{T2} - \text{NDBI}_{T1}$.

The classifier evaluates each valid pixel $p \in M_{\text{valid}}$ across a hierarchical decision tree:

```
IF (NDWI_T2 > 0.0 AND NDWI_T1 <= 0.0) OR (ΔNDWI > +0.25):
    Class = 4 (Water Inundation / Expansion)
ELSE IF (NDWI_T1 > 0.0 AND NDWI_T2 <= 0.0) OR (ΔNDWI < -0.25):
    Class = 5 (Water Body Decline / Drying)
ELSE IF (ΔNDBI > +0.20 AND ΔNDVI < -0.10):
    Class = 1 (New Built-up & Paved Infrastructure)
ELSE IF (ΔNDVI > +0.20):
    Class = 2 (Vegetation / Canopy Growth)
ELSE IF (ΔNDVI < -0.20):
    Class = 3 (Vegetation Loss / Land Clearing)
ELSE:
    Class = 0 (No Significant Change)
```

### Why Coupled Thresholds?
Urban expansion frequently replaces agricultural vegetation or bare soil with concrete. Requiring both positive $\Delta\text{NDBI} > 0.20$ and negative $\Delta\text{NDVI} < -0.10$ prevents bare summer fallow land from being falsely flagged as new urban construction.

---

## 4. Minimum Mapping Unit (MMU) Morphological Filter

Raw pixel-level thresholding inevitably generates **salt-and-pepper noise** due to:
- Sub-pixel coregistration jitter ($\le 0.5$ pixel).
- Solar illumination angle differences between seasons.
- Sensor detector micro-variations.

To eliminate noise, SatQuery AI applies a **Minimum Mapping Unit (MMU) filter**:
1. Groups contiguous 8-connected pixels of the same change class into spatial polygon components: $\mathcal{C}_k = \{p_1, p_2, \dots, p_N\}$.
2. Evaluates cluster cardinality against threshold $\text{MMU} = 9\text{ pixels}$.
3. Discards any component where $|\mathcal{C}_k| < 9$:
   $$
   M_{\text{cleaned}}(p) = 
   \begin{cases}
   M(p) & \text{if } |\mathcal{C}_k| \ge 9 \\
   0 & \text{if } |\mathcal{C}_k| < 9
   \end{cases}
   $$
4. At $10\,\text{m}$ GSD, $9\text{ pixels} = 30\,\text{m} \times 30\,\text{m} = 900\,\text{m}^2 = 0.09\,\text{hectares}$. This corresponds to the physical footprint of an individual building or roadway segment, ensuring that only verified ground-truth structures are counted.

---

## 5. Physical Hectare Conversion

At Sentinel-2 MSI's native 10-meter Ground Sampling Distance (GSD):
$$
\text{Pixel Area} = 10\,\text{m} \times 10\,\text{m} = 100\,\text{m}^2
$$
$$
1\,\text{hectare} = 10\,000\,\text{m}^2 \implies 1\text{ pixel} = 0.01\,\text{ha}
$$

For any classified category $c \in \{1, 2, 3, 4, 5\}$:
$$
\text{Area}_c (\text{ha}) = N_{\text{pixels}}(c) \times 0.01\,\text{ha}
$$
$$
\text{Total Changed Area} = \sum_{c=1}^5 \text{Area}_c (\text{ha})
$$
$$
\text{Coverage Percentage} = \frac{\text{Total Changed Area}}{\text{AOI Total Area}} \times 100\%
$$

All calculations are executed in 64-bit precision and rounded to 1 decimal place for reporting clarity.
