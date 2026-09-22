"""
SatQuery AI - Location & Geocoding Service
Converts natural-language place names or coordinates to geographic bounding boxes
using OpenStreetMap Nominatim with caching, rate-limiting, and large-AOI safeguards.
"""

import math
import time
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
CACHE_TTL_SECONDS = 86400  # 24 hours


class LocationService:
    def __init__(self):
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._last_request_time: float = 0.0
        
        # Pre-indexed reference catalog for instant zero-network demo and test execution
        self._local_registry: Dict[str, Dict[str, Any]] = {
            "gudlavalleru": {
                "name": "Gudlavalleru",
                "display_name": "Gudlavalleru, Krishna District, Andhra Pradesh, India",
                "lat": 16.0200,
                "lon": 80.7000,
                "bbox": [80.6500, 15.9800, 80.7500, 16.0800],
                "type": "village"
            },
            "machilipatnam": {
                "name": "Machilipatnam",
                "display_name": "Machilipatnam Deepwater Port & Town, Andhra Pradesh, India",
                "lat": 16.1871,
                "lon": 81.1348,
                "bbox": [81.0800, 16.1400, 81.1900, 16.2400],
                "type": "port_town"
            },
            "vijayawada": {
                "name": "Vijayawada",
                "display_name": "Vijayawada, Krishna District, Andhra Pradesh, India",
                "lat": 16.5100,
                "lon": 80.6500,
                "bbox": [80.5800, 16.4500, 80.7100, 16.5700],
                "type": "city"
            },
            "avanigadda": {
                "name": "Avanigadda",
                "display_name": "Avanigadda, Krishna River Delta, Andhra Pradesh, India",
                "lat": 16.0193,
                "lon": 80.9151,
                "bbox": [80.8500, 15.9500, 80.9800, 16.0800],
                "type": "town"
            },
            "visakhapatnam": {
                "name": "Visakhapatnam",
                "display_name": "Visakhapatnam Port & City, Andhra Pradesh, India",
                "lat": 17.6900,
                "lon": 83.2200,
                "bbox": [83.1500, 17.6200, 83.3200, 17.7500],
                "type": "city"
            },
            "vizag": {
                "name": "Visakhapatnam",
                "display_name": "Visakhapatnam Port & City, Andhra Pradesh, India",
                "lat": 17.6900,
                "lon": 83.2200,
                "bbox": [83.1500, 17.6200, 83.3200, 17.7500],
                "type": "city"
            },
            "amaravati": {
                "name": "Amaravati",
                "display_name": "Amaravati Capital Region, Andhra Pradesh, India",
                "lat": 16.5400,
                "lon": 80.5100,
                "bbox": [80.4500, 16.4800, 80.5800, 16.6000],
                "type": "city"
            },
            "tirupati": {
                "name": "Tirupati",
                "display_name": "Tirupati & Seshachalam Foothills, Andhra Pradesh, India",
                "lat": 13.6300,
                "lon": 79.4200,
                "bbox": [79.3500, 13.5600, 79.4800, 13.7000],
                "type": "city"
            },
            "guntur": {
                "name": "Guntur",
                "display_name": "Guntur, Andhra Pradesh, India",
                "lat": 16.3100,
                "lon": 80.4400,
                "bbox": [80.3700, 16.2400, 80.5000, 16.3700],
                "type": "city"
            },
            "rajahmundry": {
                "name": "Rajahmundry",
                "display_name": "Rajahmundry & Godavari River, Andhra Pradesh, India",
                "lat": 17.0000,
                "lon": 81.8000,
                "bbox": [81.7400, 16.9400, 81.8700, 17.0600],
                "type": "city"
            },
            "kakinada": {
                "name": "Kakinada",
                "display_name": "Kakinada Port & Coast, Andhra Pradesh, India",
                "lat": 16.9900,
                "lon": 82.2500,
                "bbox": [82.1800, 16.9200, 82.3100, 17.0500],
                "type": "city"
            },
            "kurnool": {
                "name": "Kurnool",
                "display_name": "Kurnool Tungabhadra Basin, Andhra Pradesh, India",
                "lat": 15.8300,
                "lon": 78.0400,
                "bbox": [77.9700, 15.7600, 78.1000, 15.8900],
                "type": "city"
            },
            "hyderabad": {
                "name": "Hyderabad",
                "display_name": "Hyderabad, Telangana, India",
                "lat": 17.3850,
                "lon": 78.4867,
                "bbox": [78.3800, 17.3000, 78.5800, 17.4800],
                "type": "metropolis"
            }
        }

    def search_place(self, query: str) -> Dict[str, Any]:
        """
        Geocodes a query string to standard coordinates and bounding box [min_lon, min_lat, max_lon, max_lat].
        Accepts: Place names ('Vijayawada', 'Machilipatnam'), landmarks, or coordinate pairs ('16.02, 80.70').
        """
        raw_q = query.strip()
        cleaned_key = raw_q.lower()

        # 1. Coordinate pair check: e.g. "16.0200, 80.7000" or "16.02N 80.70E"
        coord_res = self._try_parse_coordinates(raw_q)
        if coord_res:
            return coord_res

        # 2. Check in-memory cache
        if cleaned_key in self._cache:
            ts, res = self._cache[cleaned_key]
            if time.time() - ts < CACHE_TTL_SECONDS:
                return res

        # 3. Check local reference registry
        for key, reg in self._local_registry.items():
            if cleaned_key == key or key in cleaned_key or cleaned_key in key:
                result = self._format_location_result(
                    name=reg["name"],
                    display_name=reg["display_name"],
                    lat=reg["lat"],
                    lon=reg["lon"],
                    bbox=reg["bbox"],
                    source="local_catalog"
                )
                self._cache[cleaned_key] = (time.time(), result)
                return result

        # 4. Query live OpenStreetMap Nominatim
        nominatim_res = self._query_nominatim(raw_q)
        if nominatim_res:
            self._cache[cleaned_key] = (time.time(), nominatim_res)
            return nominatim_res

        # 5. Default fallback to Gudlavalleru if all lookups fail
        fallback = self._local_registry["gudlavalleru"]
        return self._format_location_result(
            name="Gudlavalleru (Default)",
            display_name=fallback["display_name"],
            lat=fallback["lat"],
            lon=fallback["lon"],
            bbox=fallback["bbox"],
            source="fallback_default"
        )

    def _query_nominatim(self, place_name: str) -> Optional[Dict[str, Any]]:
        # Enforce rate limit (at least 0.5s between queries)
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        self._last_request_time = time.time()

        params = {
            "q": place_name,
            "format": "json",
            "limit": 3,
            "addressdetails": 1
        }
        url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SatQueryAI-SIH2026/2.0 (ISRO PS 26167)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data and len(data) > 0:
                        first = data[0]
                        lat = float(first["lat"])
                        lon = float(first["lon"])
                        # Nominatim bbox is [min_lat, max_lat, min_lon, max_lon]
                        nb = [float(x) for x in first["boundingbox"]]
                        # Standardize to [min_lon, min_lat, max_lon, max_lat]
                        std_bbox = [nb[2], nb[0], nb[3], nb[1]]
                        
                        return self._format_location_result(
                            name=first.get("name") or place_name,
                            display_name=first.get("display_name", place_name),
                            lat=lat,
                            lon=lon,
                            bbox=std_bbox,
                            source="osm_nominatim"
                        )
        except Exception as err:
            logger.debug(f"Nominatim query failed ({err}); proceeding with catalog fallback.")

        return None

    def _try_parse_coordinates(self, text: str) -> Optional[Dict[str, Any]]:
        cleaned = text.replace("°", "").replace("N", "").replace("E", "").replace("S", "-").replace("W", "-")
        if "," in cleaned:
            parts = [p.strip() for p in cleaned.split(",")]
        elif " " in cleaned:
            parts = [p.strip() for p in cleaned.split()]
        else:
            return None

        if len(parts) == 2:
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    # Construct nominal 10km x 10km AOI around point (~0.05 deg)
                    d = 0.05
                    bbox = [round(lon - d, 4), round(lat - d, 4), round(lon + d, 4), round(lat + d, 4)]
                    return self._format_location_result(
                        name=f"Coordinate ({lat:.4f}, {lon:.4f})",
                        display_name=f"Location at Lat {lat:.4f}°, Lon {lon:.4f}°",
                        lat=lat,
                        lon=lon,
                        bbox=bbox,
                        source="coordinates_input"
                    )
            except ValueError:
                pass
        return None

    def _format_location_result(
        self,
        name: str,
        display_name: str,
        lat: float,
        lon: float,
        bbox: List[float],
        source: str
    ) -> Dict[str, Any]:
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Calculate approximate area in km2
        # 1 deg lat ~ 111.32 km, 1 deg lon ~ 111.32 * cos(lat) km
        width_km = abs(max_lon - min_lon) * 111.32 * math.cos(math.radians(lat))
        height_km = abs(max_lat - min_lat) * 111.32
        area_km2 = round(width_km * height_km, 1)

        is_large = area_km2 > 500.0
        warning = (
            f"Selected AOI is large ({area_km2:.0f} km²). For high-speed analysis, "
            "choose an area under 500 km²."
            if is_large else None
        )

        return {
            "name": name,
            "place": name,
            "display_name": display_name,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "coordinates_display": f"{lat:.4f}° N, {lon:.4f}° E" if lat >= 0 else f"{abs(lat):.4f}° S, {lon:.4f}° E",
            "bbox": [round(x, 4) for x in bbox],
            "bbox_latlon": [round(min_lat, 4), round(min_lon, 4), round(max_lat, 4), round(max_lon, 4)],
            "bbox_display": f"[{min_lon:.2f}, {min_lat:.2f}, {max_lon:.2f}, {max_lat:.2f}]",
            "width_km": round(width_km, 1),
            "height_km": round(height_km, 1),
            "area_km2": area_km2,
            "is_large_aoi": is_large,
            "warning": warning,
            "source": source
        }

    search_location = search_place


location_service = LocationService()
