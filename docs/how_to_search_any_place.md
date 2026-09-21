# How to Search Any Place in SatQuery AI

**Smart India Hackathon 2026 | Problem Statement ID: 26167**  
**Theme:** Space Technology | **ISRO / SAC**

---

## 1. Overview

SatQuery AI is designed to break free from static, hard-coded demonstration areas. While it ships with three verified high-resolution ground-truth competition packages (Gudlavalleru, Machilipatnam, Godavari Basin), the platform is equipped with an **end-to-end global and national place search engine** powered by:

1. **Nominatim (OpenStreetMap) Geocoding Engine**: Translates any natural language place name (village, town, city, district, landmark) into precision WGS84 geographic coordinates and a bounding box (`[min_lon, min_lat, max_lon, max_lat]`).
2. **Copernicus Data Space Ecosystem (CDSE) STAC & OData APIs**: Queries the European Space Agency's free Sentinel-2 Level-2A (Bottom-Of-Atmosphere reflectance) global catalog.
3. **Local Fallback & Cached Tile Store**: Guarantees zero downtime during presentations even if external public APIs experience network rate-limiting.

---

## 2. Step-by-Step Guide: Searching Any Location

### Method A: Quick Search via Andhra Pradesh State Catalog
If searching for places across Andhra Pradesh:
1. In the **Mission Control Dashboard**, locate the **Andhra Pradesh State-Wide Coverage** card on the left panel.
2. Click any of the quick-action pills:
   - **Gudlavalleru** (Urban growth & paving)
   - **Machilipatnam** (Deepwater port construction & breakwater)
   - **Godavari Flood** (Monsoon basin inundation)
   - **Vijayawada** (Krishna River corridor & Prakasam Barrage)
   - **Amaravati** (Capital region governmental complex)
   - **Visakhapatnam** (Smart city & coastal harbor)
   - **Tirupati** (Foothill transit infrastructure)
   - **Entire AP** (State-wide regional macro mosaic)
3. Or type the name into the **Search AP** input box (e.g., `Avanigadda`, `Guntur`, `Kurnool`, `Nellore`) and press **Enter** or click **Locate**.
4. The Tactical Coordinates HUD immediately updates with the exact latitude, longitude, and bounding box, and the satellite scenes are loaded into the viewport.

---

### Method B: Live Global Search via Copernicus CDSE
To search any location in India or worldwide:
1. Click the **Copernicus Live** tab in the left sidebar.
2. In the **Place Name** input field, type any location name, for example:
   - `Vijayawada`
   - `Avanigadda`
   - `Kakinada Port`
   - `Varanasi`
   - `Mumbai Harbour`
   - `Paris`
3. Adjust the **Max Cloud Cover** slider (default: `20%`).
4. Click **Search Copernicus**.
5. The system performs:
   - Real-time geocoding query to resolve the exact bounding box.
   - Live query to `catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json` or STAC API.
   - Extraction of recent Sentinel-2 Level-2A MSI acquisitions.
6. The results list displays all matching scenes with:
   - Scene Product ID
   - Acquisition Date (e.g., `2026-09-02`)
   - Cloud Cover Percentage
   - Scene Coordinates & Bounding Box
   - Visual Thumbnail Preview
7. If two or more scenes are found across different dates, a **Bi-Temporal Pair Available** banner appears with a **Load Both Scenes for Change Detection** button.
8. Click **Load Scene** or **Load Both Scenes**, then click **Analyze Satellite Images** to execute the multi-band raster processing pipeline.

---

## 3. Backend Endpoints for Location Search

SatQuery AI exposes standardized REST endpoints for programmatic place search:

### 1. AOI Geocode Search
```http
GET /api/v1/aoi/search?q={place_name}
```
**Example Response:**
```json
{
  "status": "success",
  "query": "avanigadda",
  "aoi": "avanigadda",
  "display_name": "Avanigadda, Krishna River Delta, Andhra Pradesh, India",
  "center": {
    "lat": 16.0193,
    "lon": 80.9151
  },
  "bbox": [15.95, 80.85, 16.08, 80.98],
  "source": "osm_nominatim"
}
```

### 2. Copernicus Live Scenes Query
```http
GET /api/copernicus/scenes?aoi_name={place_name}&max_cloud={0-100}
```
**Example Response:**
```json
{
  "status": "success",
  "aoi": "Vijayawada",
  "latitude": 16.51,
  "longitude": 80.65,
  "coordinates_display": "16.5100° N, 80.6500° E",
  "bbox": [16.45, 80.58, 16.57, 80.71],
  "bbox_display": "[16.45, 80.58, 16.57, 80.71]",
  "count": 4,
  "scenes": [
    {
      "id": "S2B_MSIL2A_20260902T050649_N0511_R019_T44QKE",
      "date": "2026-09-02",
      "cloud_cover": 2.4,
      "thumbnail_url": "/static/thumbs/vja_s2_2026_09_02.jpg",
      "coordinates_display": "16.5100° N, 80.6500° E"
    },
    {
      "id": "S2A_MSIL2A_20250815T051021_N0510_R019_T44QKE",
      "date": "2025-08-15",
      "cloud_cover": 4.1,
      "thumbnail_url": "/static/thumbs/vja_s2_2025_08_15.jpg",
      "coordinates_display": "16.5100° N, 80.6500° E"
    }
  ]
}
```

---

## 4. Resilience & Fallback Architecture

To ensure flawless demonstrations under hackathon conditions:
1. **Network Timeout Guard:** External API requests are bounded with a 5.0-second timeout.
2. **Local Scene Cache:** If the external Copernicus network is unreachable or throttled, the backend automatically serves verified local Sentinel-2 L2A tiles matching the queried district.
3. **Coordinate Integrity:** Every displayed scene maintains explicit coordinate provenance (`EPSG:4326`, Lat/Lon, Bounding Box), ensuring that no generic or unreferenced images are presented to judges.
