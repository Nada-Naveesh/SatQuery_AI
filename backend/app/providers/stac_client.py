"""
SatQuery AI - Copernicus STAC Catalog Client
Queries Copernicus Data Space Ecosystem STAC API for Sentinel-2 Level-2A products.
"""

import json
import logging
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.app.providers.copernicus_auth import copernicus_auth
from backend.app.providers.provider_models import CopernicusScene

logger = logging.getLogger(__name__)

STAC_ENDPOINT = "https://catalogue.dataspace.copernicus.eu/stac/search"
RESTO_CATALOG_ENDPOINT = "https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json"


class CopernicusSTACClient:
    def __init__(self, timeout_seconds: float = 6.0):
        self.timeout = timeout_seconds

    def search_scenes(
        self,
        bbox: List[float],
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        max_cloud: float = 25.0,
        limit: int = 10
    ) -> List[CopernicusScene]:
        """
        Executes a live query to the Copernicus STAC / Resto catalog for Sentinel-2 L2A scenes.
        bbox format: [min_lon, min_lat, max_lon, max_lat]
        """
        token = copernicus_auth.get_token()
        headers = {
            "User-Agent": "SatQueryAI-SIH2026/2.0 (ISRO PS 26167)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        min_lon, min_lat, max_lon, max_lat = bbox

        # Construct STAC search payload
        d_from = date_from or "2024-01-01T00:00:00Z"
        d_to = date_to or datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")
        if "T" not in d_from:
            d_from = f"{d_from}T00:00:00Z"
        if "T" not in d_to:
            d_to = f"{d_to}T23:59:59Z"

        stac_payload = {
            "collections": ["SENTINEL-2"],
            "bbox": [min_lon, min_lat, max_lon, max_lat],
            "datetime": f"{d_from}/{d_to}",
            "query": {
                "cloudCover": {"lte": float(max_cloud)},
                "productType": {"eq": "S2MSI2A"}
            },
            "limit": limit,
            "sortby": [{"field": "properties.datetime", "direction": "desc"}]
        }

        # Try STAC API first
        try:
            req = urllib.request.Request(
                STAC_ENDPOINT,
                data=json.dumps(stac_payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    features = data.get("features", [])
                    scenes = self._parse_stac_features(features, bbox)
                    if scenes:
                        logger.info(f"Retrieved {len(scenes)} live scenes from Copernicus STAC endpoint.")
                        return scenes
        except Exception as e:
            logger.debug(f"Copernicus STAC POST query failed ({e}); attempting RESTO fallback.")

        # Try GET query on Resto catalog API as secondary live endpoint
        try:
            resto_url = (
                f"{RESTO_CATALOG_ENDPOINT}?box={min_lon},{min_lat},{max_lon},{max_lat}"
                f"&startDate={d_from[:10]}&completionDate={d_to[:10]}"
                f"&maxRecords={limit}&productType=S2MSI2A"
            )
            resto_req = urllib.request.Request(
                resto_url,
                headers={"User-Agent": "SatQueryAI-SIH2026/2.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(resto_req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    features = data.get("features", [])
                    scenes = self._parse_resto_features(features, bbox)
                    if scenes:
                        logger.info(f"Retrieved {len(scenes)} live scenes from Copernicus Resto endpoint.")
                        return scenes
        except Exception as e:
            logger.debug(f"Copernicus Resto query failed ({e}).")

        return []

    def _parse_stac_features(self, features: List[Dict[str, Any]], bbox: List[float]) -> List[CopernicusScene]:
        scenes: List[CopernicusScene] = []
        for f in features:
            props = f.get("properties", {})
            scene_id = f.get("id") or props.get("title") or "S2_SCENE"
            dt_str = props.get("datetime") or props.get("start_datetime") or ""
            date = dt_str[:10] if len(dt_str) >= 10 else datetime.utcnow().strftime("%Y-%m-%d")
            cloud = float(props.get("cloudCover") or props.get("eo:cloud_cover") or 0.0)
            platform = props.get("platform") or "Sentinel-2"
            
            # Asset quicklook
            assets = f.get("assets", {})
            quicklook = (
                assets.get("thumbnail", {}).get("href")
                or assets.get("overview", {}).get("href")
                or assets.get("visual", {}).get("href")
                or f"/static/thumbs/{scene_id[:16]}.jpg"
            )

            scenes.append(CopernicusScene(
                id=scene_id,
                date=date,
                cloud_cover=round(cloud, 1),
                platform=platform,
                processing_level="L2A",
                footprint=f.get("geometry"),
                quicklook_url=quicklook,
                bbox=bbox,
                valid_for_comparison=cloud <= 30.0,
                warnings=[f"Cloud cover is {cloud:.1f}%"] if cloud > 20.0 else []
            ))
        return scenes

    def _parse_resto_features(self, features: List[Dict[str, Any]], bbox: List[float]) -> List[CopernicusScene]:
        scenes: List[CopernicusScene] = []
        for f in features:
            props = f.get("properties", {})
            scene_id = props.get("title") or f.get("id") or "S2_SCENE"
            dt_str = props.get("startDate") or ""
            date = dt_str[:10] if len(dt_str) >= 10 else datetime.utcnow().strftime("%Y-%m-%d")
            cloud = float(props.get("cloudCover") or 0.0)
            quicklook = props.get("quicklook") or props.get("thumbnail") or f"/static/thumbs/{scene_id[:16]}.jpg"

            scenes.append(CopernicusScene(
                id=scene_id,
                date=date,
                cloud_cover=round(cloud, 1),
                platform="Sentinel-2",
                processing_level="L2A",
                footprint=f.get("geometry"),
                quicklook_url=quicklook,
                bbox=bbox,
                valid_for_comparison=cloud <= 30.0,
                warnings=[f"Cloud cover is {cloud:.1f}%"] if cloud > 20.0 else []
            ))
        return scenes


stac_client = CopernicusSTACClient()
