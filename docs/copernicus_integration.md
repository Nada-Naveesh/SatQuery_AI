# Copernicus Data Space Ecosystem (CDSE) Ingestion & Discovery

**SatQuery AI — Autonomous Vision-Language Satellite Intelligence**  
**Smart India Hackathon 2026 | Problem Statement 26167 | ISRO / Space Applications Centre (SAC)**

---

## 1. Overview & Objective

SatQuery AI integrates directly with the **Copernicus Data Space Ecosystem (CDSE)** to provide automated discovery, acquisition, and ingestion of European Space Agency (ESA) **Sentinel-2 MultiSpectral Instrument (MSI)** Level-2A Bottom-Of-Atmosphere (BOA) reflectance scenes.

Unlike traditional static hackathon prototypes that rely exclusively on pre-clipped, hardcoded rasters, SatQuery AI features a **dynamic two-tier geospatial acquisition pipeline**:
1. **Live CDSE OData / STAC API querying**: Dynamically searches Sentinel-2 L2A constellations over any user-specified Area of Interest (AOI) anywhere on Earth, with geographic polygon clipping, date filtering, and cloud-cover thresholding.
2. **Deterministic Offline Cache & Fallback**: Automatically activates if internet connectivity is restricted during hackathon defense rounds, providing sub-millisecond retrieval of pre-calibrated multi-spectral scenes across 11 key regions in Andhra Pradesh and major Indian corridors.

---

## 2. API Endpoints

### `GET /api/copernicus/scenes` / `GET /api/v1/copernicus/scenes`

Discovers Sentinel-2 L2A optical scenes matching geographic, temporal, and atmospheric criteria.

#### Query Parameters:
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `aoi_name` | `string` | `"Gudlavalleru"` | Name of city, district, port, or landmark (e.g. `Gudlavalleru`, `Vijayawada`, `Visakhapatnam`, `Tirupati`, `Amaravati`) |
| `bbox` | `string` | `None` | Optional comma-separated bounding box `[min_lat, min_lon, max_lat, max_lon]` |
| `date_from` | `string` | `None` | Acquisition start date in `YYYY-MM-DD` |
| `date_to` | `string` | `None` | Acquisition end date in `YYYY-MM-DD` |
| `max_cloud`| `float` | `30.0` | Maximum acceptable cloud cover percentage (0.0 - 100.0) |
| `limit` | `integer`| `10` | Maximum candidate scenes to retrieve |

#### Example Request:
```bash
curl -X GET "http://localhost:8000/api/copernicus/scenes?aoi_name=Visakhapatnam&max_cloud=15&limit=5"
```

#### Example Response:
```json
{
  "provider": "Copernicus Sentinel-2 L2A (Live CDSE Stream)",
  "aoi": "Visakhapatnam",
  "display_name": "Visakhapatnam Deepwater Port & Coastal Corridor, AP, India",
  "center": {
    "lat": 17.69,
    "lon": 83.22
  },
  "bbox": [17.62, 83.15, 17.75, 83.32],
  "total_scenes": 2,
  "scenes": [
    {
      "id": "S2A_MSIL2A_20260902T050121_N0511_R033_T44QPD_20260902T083419",
      "date": "2026-09-02",
      "cloud_cover": 2.4,
      "thumbnail_url": "/static/thumbs/visakhapatnam_2026_09_02.jpg",
      "download_url": "https://dataspace.copernicus.eu/browser/?zoom=13&lat=17.69&lng=83.22",
      "processing_level": "Level-2A (BOA Reflectance)",
      "sensor": "Sentinel-2 MSI",
      "resolution_m": 10.0,
      "source": "Copernicus Data Space Ecosystem"
    }
  ]
}
```

---

## 3. Architecture & Geocoding Pipeline

```
+-------------------------------------------------------------+
|                User / Mission Control Query                |
|          ("Visakhapatnam", "Amaravati", or Custom BBox)     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|              CopernicusService.search_scenes                |
|                                                             |
|  1. Geographic Resolution:                                  |
|     - Check Indian High-Resolution GEO_REGISTRY             |
|     - If not found, resolve via OpenStreetMap Nominatim     |
|                                                             |
|  2. Live CDSE Ingestion:                                    |
|     - Query Copernicus OData API with WKT POLYGON & filter   |
|     - If live response received within timeout:             |
|       Format & return real-time scene candidates             |
|                                                             |
|  3. Resilient Fallback Engine:                              |
|     - If offline/firewalled: query local GeoTIFF catalog    |
|     - Synthesize authentic bi-temporal metadata for testing |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                 Agent Controller Multi-Tool                 |
|             (VQA, Change Detection, SAR Fusion)             |
+-------------------------------------------------------------+
```

---

## 4. Setup Copernicus CDSE API Credentials (Optional)

By default, SatQuery AI provides **instant zero-setup operation** using public catalog discovery and local high-resolution GeoTIFF caches. For full authenticated streaming of entire 500MB+ SAFE zip products from the Copernicus Hub:

1. Register for a free account at [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/).
2. Navigate to your **Account Settings** -> **OAuth Clients**.
3. Generate a Client ID and Client Secret.
4. Add the credentials to your `.env` file:
   ```env
   COPERNICUS_CLIENT_ID=your_client_id_here
   COPERNICUS_CLIENT_SECRET=your_client_secret_here
   COPERNICUS_BASE_URL=https://catalogue.dataspace.copernicus.eu/odata/v1
   ```
5. Restart SatQuery AI backend:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

---

## 5. Free Satellite Imagery Download Guide for Judges & Operators

For operators wishing to ingest new custom GeoTIFF scenes into SatQuery AI:

1. **Copernicus Browser (ESA Sentinel-1 & Sentinel-2)**:
   - Visit: [https://dataspace.copernicus.eu/browser/](https://dataspace.copernicus.eu/browser/)
   - Search your target AOI (e.g., Godavari Delta, Vijayawada, Krishna River).
   - Select **Sentinel-2 L2A** (True Color RGB + NIR Bands 2, 3, 4, 8).
   - Click **Download** or download analytical GeoTIFFs (10m GSD).
2. **USGS EarthExplorer (Landsat 8/9)**:
   - Visit: [https://earthexplorer.usgs.gov/](https://earthexplorer.usgs.gov/)
   - Free global 30m multi-spectral imagery.
3. **ISRO Bhoovan / Open Data Archive**:
   - Visit: [https://bhuvan.nrsc.gov.in/](https://bhuvan.nrsc.gov.in/)
   - Access Resourcesat and Cartosat optical archives over Indian territories.

Drag and drop any downloaded GeoTIFF directly into the **Custom Image Upload** panel in the SatQuery AI Mission Control UI to immediately execute agentic multimodal reasoning.
