"""
SatQuery AI - Unified Copernicus Data Space Ecosystem Provider
Coordinates STAC discovery, scene validation, and calibrated remote-sensing ingestion.
"""

import logging
from typing import List, Optional, Dict, Any

from backend.app.providers.provider_models import CopernicusScene, CopernicusSearchResponse, SceneValidationResult
from backend.app.providers.stac_client import stac_client
from backend.app.providers.copernicus_auth import copernicus_auth
from backend.app.services.copernicus_service import copernicus_service

logger = logging.getLogger(__name__)


class CopernicusProvider:
    def __init__(self):
        self.auth = copernicus_auth
        self.stac = stac_client

    def check_connection(self) -> Dict[str, Any]:
        """Performs a live connectivity check to Copernicus CDSE."""
        has_creds = self.auth.has_credentials
        token_active = self.auth.get_token() is not None if has_creds else False
        
        # Test basic catalog reachability (timeout 3s)
        catalog_reachable = False
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://catalogue.dataspace.copernicus.eu/stac",
                headers={"User-Agent": "SatQueryAI-HealthCheck/2.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                catalog_reachable = (resp.status == 200)
        except Exception:
            catalog_reachable = False

        status = "connected" if (catalog_reachable or token_active) else "offline"
        return {
            "status": status,
            "catalog_reachable": catalog_reachable,
            "authenticated": token_active,
            "has_credentials": has_creds,
            "collection": "SENTINEL-2 (L2A MSI BOA)"
        }

    def search_scenes_for_aoi(
        self,
        aoi_name: str,
        bbox: List[float],
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        max_cloud: float = 25.0,
        limit: int = 10
    ) -> CopernicusSearchResponse:
        """
        Discovers real Sentinel-2 Level-2A scenes for the provided bounding box.
        Tries live STAC query first. If external network is unreachable or rate-limited,
        gracefully returns pre-indexed regional Sentinel-2 L2A scenes with honest provenance.
        """
        # 1. Attempt live STAC search
        live_scenes = self.stac.search_scenes(
            bbox=bbox,
            date_from=date_from,
            date_to=date_to,
            max_cloud=max_cloud,
            limit=limit
        )

        min_lon, min_lat, max_lon, max_lat = bbox
        center_lat = round((min_lat + max_lat) / 2.0, 4)
        center_lon = round((min_lon + max_lon) / 2.0, 4)
        coords_str = f"{center_lat:.4f}° N, {center_lon:.4f}° E"
        bbox_str = f"[{min_lon:.2f}, {min_lat:.2f}, {max_lon:.2f}, {max_lat:.2f}]"

        if live_scenes:
            for sc in live_scenes:
                sc.coordinates_display = coords_str
                sc.bbox_display = bbox_str
                sc.bbox = bbox

            return CopernicusSearchResponse(
                provider="Copernicus Data Space Ecosystem (Live STAC)",
                collection="Sentinel-2 Level-2A",
                aoi=aoi_name,
                bbox=bbox,
                latitude=center_lat,
                longitude=center_lon,
                coordinates_display=coords_str,
                bbox_display=bbox_str,
                count=len(live_scenes),
                scenes=live_scenes,
                is_live_query=True
            )

        # 2. Fallback to pre-indexed regional Sentinel-2 L2A catalog
        # Matches against the existing copernicus_service catalog
        fallback_data = copernicus_service.search_scenes(
            aoi_name=aoi_name,
            max_cloud_cover=max_cloud,
            limit=limit
        )

        scenes_models: List[CopernicusScene] = []
        for sc in fallback_data.get("scenes", []):
            scenes_models.append(CopernicusScene(
                id=sc["id"],
                date=sc["date"],
                cloud_cover=sc.get("cloud_cover", 5.0),
                platform="Sentinel-2",
                processing_level="L2A",
                quicklook_url=sc.get("thumbnail_url", "/static/thumbs/vja_s2_2026_09_02.jpg"),
                coordinates_display=sc.get("coordinates_display") or coords_str,
                bbox_display=sc.get("bbox_display") or bbox_str,
                bbox=bbox,
                valid_for_comparison=True,
                warnings=[]
            ))

        return CopernicusSearchResponse(
            provider="Copernicus Data Space Ecosystem (Sentinel-2 BOA)",
            collection="Sentinel-2 Level-2A",
            aoi=aoi_name,
            bbox=bbox,
            latitude=center_lat,
            longitude=center_lon,
            coordinates_display=coords_str,
            bbox_display=bbox_str,
            count=len(scenes_models),
            scenes=scenes_models,
            is_live_query=False
        )


copernicus_provider = CopernicusProvider()
