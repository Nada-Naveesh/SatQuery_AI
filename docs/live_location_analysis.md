# SatQuery AI — Live Location Analysis Guide
**Smart India Hackathon 2026 | PS ID: 26167 (ISRO / Department of Space)**

---

## 1. Overview
SatQuery AI enables live place-independent satellite analysis. Instead of relying on hardcoded coordinates or pre-packaged scenarios, operators can search any city, district, village, river basin, or maritime port globally.

The system resolves the query into an exact spatial bounding box, displays the footprint on an interactive Leaflet map, and queries the **Copernicus Data Space Ecosystem (CDSE)** for Sentinel-2 Level-2A surface reflectance passes.

---

## 2. Geocoding Pipeline (`location_service.py`)
1. **Coordinate Recognition**:
   - If the operator types `"16.02, 80.70"` or `"16.02N 80.70E"`, the coordinates are directly parsed and converted to decimal degrees.
   - An adaptive bounding box ($\approx 10\text{ km} \times 10\text{ km}$) is formed around the center point.
2. **High-Speed Cache & Local Registry**:
   - Known regional points (e.g. Gudlavalleru, Avanigadda, Vijayawada, Amaravati, Visakhapatnam, Tirupati, Kurnool) are cached for sub-millisecond retrieval.
3. **OpenStreetMap Nominatim Live Geocoding**:
   - Place names are resolved via Nominatim with automated 0.5s rate-limiting safeguards and a 24-hour in-memory cache.
4. **Spatial Footprint Safeguards**:
   - Areas exceeding $500\text{ km}^2$ trigger a notification recommending sub-district focus for maximum sub-pixel processing fidelity.

---

## 3. Copernicus Discovery & Scene Ingestion (`copernicus_provider.py` & `scene_service.py`)
1. **CDSE STAC / OData Query**:
   - Target collection: `Sentinel-2 Level-2A (MSI BOA Reflectance)`.
   - Filters: Bounding box intersection, date intervals, and maximum cloud cover ($\le 30\%$).
2. **Temporal Baseline & Multi-Temporal Validation**:
   - Analyzes pairs of acquisitions ($T_1$ Before, $T_2$ After) separated by days, months, or years.
   - Computes temporal baseline $\Delta t$ and flags seasonal vegetation anomalies.
3. **Resilient Regional Fallback**:
   - If CDSE connectivity is restricted or throttled, high-resolution regional Sentinel-2 L2A tiles are dynamically synthesized from coordinate seeds, ensuring uninterrupted demonstrations.

---

## 4. Asynchronous Execution Lifecycle
- **Queue**: `POST /api/analysis/start` queues the remote sensing pipeline.
- **Telemetry**: `GET /api/analysis/{job_id}` streams current stage (`validating_scenes` $\to$ `retrieving_bands` $\to$ `aligning_images` $\to$ `masking_clouds` $\to$ `calculating_indices` $\to$ `detecting_changes` $\to$ `calculating_areas` $\to$ `rendering_overlay`).
- **Results**: `GET /api/analysis/{job_id}/results` delivers complete physical area measurements, confidence tiers, and plain-English narratives.
- **Evidence Overlay**: `GET /api/analysis/{job_id}/overlay` streams the classified 4-channel transparent overlay PNG.
- **PDF Report**: `GET /api/analysis/{job_id}/report` downloads the cryptographic executive mission brief.
