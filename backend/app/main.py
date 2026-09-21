import os
import io
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.schemas import (
    AnalysisResponse,
    DemoScenario,
    InputSummary
)
from backend.app.validators import validate_upload_files
from backend.app.utils.image_io import load_image_from_bytes, load_image_from_path
from backend.app.utils.geo_utils import detect_modality_heuristics
from backend.app.utils.report_generator import generate_mission_pdf_report
from backend.app.agent.controller import controller
from backend.app.agent.registry import registry
from backend.app.services.catalog_service import catalog_service
from backend.app.services.trace_service import trace_service
from backend.app.services.copernicus_service import copernicus_service
from backend.app.mission_control import MISSION_CONTROL_HTML

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Interactive Vision-Language Assistant for Multimodal Remote Sensing (SIH 2026 PS 26167)"
)

# Enable CORS for local Next.js frontend or external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/static/demo_scenarios", StaticFiles(directory=str(settings.DEMO_SCENARIOS_DIR)), name="demo_scenarios")
LATEST_STATIC_DIR = settings.DATA_DIR / "latest"
LATEST_STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/latest", StaticFiles(directory=str(LATEST_STATIC_DIR)), name="latest")
GVL_STATIC_DIR = settings.DATA_DIR / "gudlavalleru"
if GVL_STATIC_DIR.exists():
    app.mount("/static/gudlavalleru", StaticFiles(directory=str(GVL_STATIC_DIR)), name="gudlavalleru")
AP_STATIC_DIR = settings.DATA_DIR / "andhra_pradesh"
if AP_STATIC_DIR.exists():
    app.mount("/static/andhra_pradesh", StaticFiles(directory=str(AP_STATIC_DIR)), name="andhra_pradesh")

DEMO_DATA_STATIC_DIR = settings.ROOT_DIR / "backend" / "demo_data"
DEMO_DATA_STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/demo_data", StaticFiles(directory=str(DEMO_DATA_STATIC_DIR)), name="demo_data")
app.mount("/static/demo_data", StaticFiles(directory=str(DEMO_DATA_STATIC_DIR)), name="static_demo_data")

OUTPUTS_STATIC_DIR = settings.ROOT_DIR / "outputs"
OUTPUTS_STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_STATIC_DIR)), name="outputs")
app.mount("/static/outputs", StaticFiles(directory=str(OUTPUTS_STATIC_DIR)), name="static_outputs")

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# In-memory store for session traces and cached payloads
SESSION_TRACES: Dict[str, Dict[str, Any]] = {}

def get_all_scenarios() -> List[DemoScenario]:
    """
    Dynamically loads all pre-configured real satellite demonstration scenarios
    from backend/demo_data/ and data/demo_scenarios/ with metadata.
    """
    scenarios: List[DemoScenario] = []

    # 1. Primary: 3 Verified Demo Packages in backend/demo_data/
    demo_pkg_dir = settings.ROOT_DIR / "backend" / "demo_data"
    if demo_pkg_dir.exists():
        for pkg in sorted(demo_pkg_dir.iterdir()):
            if pkg.is_dir():
                s_file = pkg / "scenario.json"
                if s_file.exists():
                    try:
                        with open(s_file, "r") as f:
                            meta = json.load(f)
                        img_paths = [
                            f"/demo_data/{pkg.name}/pre.png",
                            f"/demo_data/{pkg.name}/post.png"
                        ]
                        scenarios.append(DemoScenario(
                            id=meta.get("id", pkg.name),
                            title=meta.get("name", pkg.name.replace("_", " ").title()),
                            category=meta.get("category", "Bi-Temporal Change Analysis"),
                            description=meta.get("description", "Authentic Sentinel-2 Level-2A satellite scene."),
                            default_query=meta.get("default_query", meta.get("suggested_queries", ["Analyze satellite scene"])[0]),
                            image_paths=img_paths,
                            input_type=meta.get("input_type", "bitemporal_pair"),
                            sensor=meta.get("sensor", "Sentinel-2 Level-2A (MSI)"),
                            date=meta.get("date", "2025 vs 2026"),
                            area=meta.get("area", "Monitored Target AOI"),
                            resolution=meta.get("resolution", "10 m GSD"),
                            crs=meta.get("crs", "EPSG:4326"),
                            suggested_queries=meta.get("suggested_queries", []),
                            real_data_source=meta.get("real_data_source", "Copernicus Sentinel-2 L2A Archive")
                        ))
                    except Exception as err:
                        print(f"Warning: Failed to load demo package {pkg.name}: {err}")

    # 2. Secondary: Pre-existing scenarios under data/demo_scenarios/
    demo_dir = settings.DEMO_SCENARIOS_DIR
    if demo_dir.exists():
        for s_folder in sorted(demo_dir.iterdir()):
            if s_folder.is_dir():
                meta_file = s_folder / "metadata.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r") as f:
                            meta = json.load(f)
                        preview_files = meta.get("preview_files", [])
                        if not preview_files:
                            preview_files = [p.name for p in sorted(s_folder.glob("*.png"))]
                        if not preview_files:
                            preview_files = [p.name for p in sorted(s_folder.glob("*.tif"))]

                        img_paths = [f"/static/demo_scenarios/{s_folder.name}/{fname}" for fname in preview_files]

                        scenarios.append(DemoScenario(
                            id=meta.get("id", s_folder.name),
                            title=meta.get("name", s_folder.name.replace("_", " ").title()),
                            category=meta.get("category", "Multimodal Remote Sensing Analysis"),
                            description=meta.get("description", f"Authentic satellite imagery ({meta.get('sensor', 'Earth Observation')}) acquired over {meta.get('area', 'Target AOI')}."),
                            default_query=meta.get("suggested_queries", ["Analyze satellite scene"])[0],
                            image_paths=img_paths,
                            input_type=meta.get("modality", "single"),
                            sensor=meta.get("sensor"),
                            date=meta.get("date"),
                            area=meta.get("area"),
                            resolution=meta.get("resolution"),
                            crs=meta.get("crs", "EPSG:4326"),
                            suggested_queries=meta.get("suggested_queries", []),
                            real_data_source=meta.get("real_data_source", "Copernicus / ISRO Open Data")
                        ))
                    except Exception as err:
                        print(f"Warning: Failed to load scenario {s_folder.name}: {err}")

    # Fallback to defaults if folder empty
    if not scenarios:
        scenarios = [
            DemoScenario(
                id="scenario_1_flood",
                title="Disaster Assessment: Inundation & Submerged Parcels",
                category="Single-Image VQA & Grounding",
                description="Sentinel-2 L2A optical acquisition over Godavari flood basin. Evaluates inundated area and delineates flood perimeters.",
                default_query="Identify the submerged agricultural parcels and highlight their spatial boundaries.",
                image_paths=["/static/samples/flood_sentinel2_optical.png"],
                input_type="single",
                sensor="Sentinel-2 L2A (MSI)",
                date="2023-07-28",
                area="Godavari River Basin, AP/Telangana, India",
                resolution="10 m GSD",
                crs="EPSG:4326",
                suggested_queries=[
                    "Identify the submerged agricultural parcels and highlight their spatial boundaries.",
                    "What is the total flooded inundation area in hectares?"
                ],
                real_data_source="Copernicus Open Access Hub / ESA Sentinel-2 L2A Archive (Tile: 44QND)"
            ),
            DemoScenario(
                id="scenario_2_urban",
                title="Temporal Change: Urban Sprawl & Infrastructure Expansion",
                category="Bi-Temporal Change Analysis (CDVQA)",
                description="Pre-construction 2022 vs Post-construction 2024 high-res optical pair. Quantifies industrial land conversion and highway paving.",
                default_query="What major infrastructure changes occurred between these two acquisition dates?",
                image_paths=["/static/samples/urban_t1_2022.png", "/static/samples/urban_t2_2024.png"],
                input_type="bitemporal_pair",
                sensor="High-Res Optical Satellite (LEVIR-CD Benchmark)",
                date="2022-04-12 (T1) vs. 2024-05-18 (T2)",
                area="Suburban Industrial Development Zone",
                resolution="0.5 m GSD",
                crs="EPSG:4326",
                suggested_queries=[
                    "What major infrastructure changes occurred between these two acquisition dates?",
                    "Has the built-up area increased?"
                ],
                real_data_source="LEVIR-CD Large-Scale Remote Sensing Change Detection Archive"
            ),
            DemoScenario(
                id="scenario_3_optical_sar",
                title="All-Weather Fusion: Cloud Penetration (Cartosat + RISAT / Sentinel-1)",
                category="Optical-SAR Cross-Modal Fusion",
                description="Cloud-occluded optical image paired with co-registered C-band SAR backscatter. Pierces cloud cover to locate metal tanks & coastline.",
                default_query="Penetrate cloud cover to map industrial storage tanks and coastal water bodies.",
                image_paths=["/static/samples/co_registered_optical_cloudy.png", "/static/samples/co_registered_sar_risat.png"],
                input_type="optical_sar_pair",
                sensor="Cartosat-2S Optical + Sentinel-1 C-band SAR",
                date="2023-08-20 (Co-registered window)",
                area="Coastal Industrial Port & Oil Storage Terminal",
                resolution="Optical 0.65m / SAR 10m GSD",
                crs="EPSG:4326",
                suggested_queries=[
                    "Penetrate cloud cover to map industrial storage tanks and coastal water bodies.",
                    "Identify built-up and water-covered regions using both optical and SAR images."
                ],
                real_data_source="ISRO SAC / ESA Sentinel-1 GRD SAR + Optical Cross-Modal Archive"
            ),
            DemoScenario(
                id="scenario_4_coastal",
                title="Coastal Change: Port Infrastructure & Breakwater Expansion",
                category="Bi-Temporal Change Analysis (CDVQA)",
                description="Visakhapatnam Port 2023 vs 2024. Evaluates marine breakwater extensions, container yard additions, and shoreline modification.",
                default_query="What new coastal infrastructure or breakwater structures were constructed between T1 and T2?",
                image_paths=["/static/demo_scenarios/scenario_4_coastal/t1.png", "/static/demo_scenarios/scenario_4_coastal/t2.png"],
                input_type="bitemporal_pair",
                sensor="Sentinel-2 L2A MSI",
                date="2023-02-15 (T1) vs. 2024-09-05 (T2)",
                area="Visakhapatnam Port & Coastal Corridor, AP, India",
                resolution="10 m GSD",
                crs="EPSG:4326",
                suggested_queries=[
                    "What new coastal infrastructure or breakwater structures were constructed between T1 and T2?",
                    "Quantify the area of newly paved port container terminal in hectares."
                ],
                real_data_source="Copernicus Open Access Hub / ESA Sentinel-2 L2A Archive"
            ),
        ]
    return scenarios


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "ps_id": settings.SIH_PS_ID,
        "organization": settings.ORGANIZATION,
        "device": settings.DEVICE,
        "registered_tools": registry.list_tools(),
        "real_data_scenarios_count": len(get_all_scenarios())
    }


@app.get("/api/scenarios", response_model=List[DemoScenario])
@app.get("/api/v1/scenarios", response_model=List[DemoScenario])
def get_scenarios():
    """Returns all available demonstration scenarios using real satellite imagery."""
    return get_all_scenarios()


@app.get("/api/scenarios/today", response_model=DemoScenario)
@app.get("/api/v1/scenarios/today", response_model=DemoScenario)
def get_todays_live_scenario():
    """Returns the freshest acquired scene from the near-real-time operational stream or catalog."""
    return catalog_service.get_todays_scenario()


@app.get("/api/scenarios/{scenario_id}", response_model=DemoScenario)
@app.get("/api/v1/scenarios/{scenario_id}", response_model=DemoScenario)
def get_scenario_detail(scenario_id: str):
    """Returns detailed real satellite metadata for a specific scenario."""
    if scenario_id in ("today", "scenario_today_near_real_time"):
        return catalog_service.get_todays_scenario()
    scenarios = get_all_scenarios()
    s = next((x for x in scenarios if x.id == scenario_id), None)
    if not s:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return s


@app.get("/api/demo-packages")
@app.get("/api/v1/demo-packages")
def list_demo_packages():
    """Returns all verified offline/competition demo packages."""
    demo_dir = settings.ROOT_DIR / "backend" / "demo_data"
    packages = []
    if demo_dir.exists():
        for pkg in sorted(demo_dir.iterdir()):
            if pkg.is_dir():
                s_file = pkg / "scenario.json"
                st_file = pkg / "statistics.json"
                q_file = pkg / "quality.json"
                pkg_data = {"id": pkg.name, "folder": pkg.name}
                if s_file.exists():
                    with open(s_file, "r") as f:
                        pkg_data["scenario"] = json.load(f)
                if st_file.exists():
                    with open(st_file, "r") as f:
                        pkg_data["statistics"] = json.load(f)
                if q_file.exists():
                    with open(q_file, "r") as f:
                        pkg_data["quality"] = json.load(f)
                pkg_data["preview_url"] = f"/demo_data/{pkg.name}/pre.png"
                pkg_data["post_url"] = f"/demo_data/{pkg.name}/post.png"
                pkg_data["overlay_url"] = f"/demo_data/{pkg.name}/change_overlay.png"
                packages.append(pkg_data)
    return {"packages": packages, "count": len(packages)}


@app.get("/api/analysis/{trace_id}")
@app.get("/api/v1/analysis/{trace_id}")
def get_analysis_output(trace_id: str):
    """Retrieves full persisted analysis output package for a given trace_id."""
    session = SESSION_TRACES.get(trace_id)
    if session:
        return session
    out_dir = settings.ROOT_DIR / "outputs" / trace_id
    if out_dir.exists() and (out_dir / "trace.json").exists():
        with open(out_dir / "trace.json", "r") as f:
            tr = json.load(f)
        stats = {}
        if (out_dir / "statistics.json").exists():
            with open(out_dir / "statistics.json", "r") as f:
                stats = json.load(f)
        return {
            "trace_id": trace_id,
            "execution_trace": tr,
            "statistics": stats,
            "overlay_url": f"/outputs/{trace_id}/change_overlay.png" if (out_dir / "change_overlay.png").exists() else None
        }
    raise HTTPException(status_code=404, detail=f"Analysis trace '{trace_id}' not found.")


AOI_REGISTRY = {
    "gudlavalleru": {
        "aoi": "gudlavalleru",
        "display_name": "Gudlavalleru, Andhra Pradesh, India",
        "center": {"lat": 16.02, "lon": 80.70},
        "bbox": [15.97, 80.65, 16.07, 80.75]
    },
    "vijayawada": {
        "aoi": "vijayawada",
        "display_name": "Vijayawada, Krishna District, Andhra Pradesh, India",
        "center": {"lat": 16.51, "lon": 80.65},
        "bbox": [16.45, 80.58, 16.57, 80.71]
    },
    "amaravati": {
        "aoi": "amaravati",
        "display_name": "Amaravati Capital Region, Andhra Pradesh, India",
        "center": {"lat": 16.54, "lon": 80.51},
        "bbox": [16.48, 80.45, 16.60, 80.58]
    },
    "visakhapatnam": {
        "aoi": "visakhapatnam",
        "display_name": "Visakhapatnam Port & Smart City, Andhra Pradesh, India",
        "center": {"lat": 17.69, "lon": 83.22},
        "bbox": [17.62, 83.15, 17.75, 83.32]
    },
    "vizag": {
        "aoi": "visakhapatnam",
        "display_name": "Visakhapatnam Port & Smart City, Andhra Pradesh, India",
        "center": {"lat": 17.69, "lon": 83.22},
        "bbox": [17.62, 83.15, 17.75, 83.32]
    },
    "tirupati": {
        "aoi": "tirupati",
        "display_name": "Tirupati & Seshachalam Foothills, Andhra Pradesh, India",
        "center": {"lat": 13.63, "lon": 79.42},
        "bbox": [13.56, 79.35, 13.70, 79.48]
    },
    "guntur": {
        "aoi": "guntur",
        "display_name": "Guntur Agricultural & Commercial Hub, Andhra Pradesh, India",
        "center": {"lat": 16.31, "lon": 80.44},
        "bbox": [16.24, 80.37, 16.37, 80.50]
    },
    "rajahmundry": {
        "aoi": "rajahmundry",
        "display_name": "Rajahmundry & Godavari River Basin, Andhra Pradesh, India",
        "center": {"lat": 17.00, "lon": 81.80},
        "bbox": [16.94, 81.74, 17.06, 81.87]
    },
    "kakinada": {
        "aoi": "kakinada",
        "display_name": "Kakinada Deepwater Port & Coringa, Andhra Pradesh, India",
        "center": {"lat": 16.99, "lon": 82.25},
        "bbox": [16.92, 82.18, 17.05, 82.31]
    },
    "kurnool": {
        "aoi": "kurnool",
        "display_name": "Kurnool Tungabhadra Basin & Solar Park, Andhra Pradesh, India",
        "center": {"lat": 15.83, "lon": 78.04},
        "bbox": [15.76, 77.97, 15.89, 78.10]
    },
    "nellore": {
        "aoi": "nellore",
        "display_name": "Nellore Pennar Basin & Aquaculture, Andhra Pradesh, India",
        "center": {"lat": 14.44, "lon": 79.99},
        "bbox": [14.38, 79.92, 14.50, 80.05]
    },
    "anantapur": {
        "aoi": "anantapur",
        "display_name": "Anantapur Semi-Arid & Renewable Belt, Andhra Pradesh, India",
        "center": {"lat": 14.68, "lon": 77.60},
        "bbox": [14.62, 77.54, 14.75, 77.66]
    },
    "avanigadda": {
        "aoi": "avanigadda",
        "display_name": "Avanigadda, Krishna River Delta, Andhra Pradesh, India",
        "center": {"lat": 16.0193, "lon": 80.9151},
        "bbox": [15.95, 80.85, 16.08, 80.98]
    },
    "andhra pradesh": {
        "aoi": "andhra_pradesh",
        "display_name": "Andhra Pradesh State Regional Mosaic, India",
        "center": {"lat": 15.91, "lon": 79.74},
        "bbox": [12.60, 76.75, 19.15, 84.75]
    },
    "ap": {
        "aoi": "andhra_pradesh",
        "display_name": "Andhra Pradesh State Regional Mosaic, India",
        "center": {"lat": 15.91, "lon": 79.74},
        "bbox": [12.60, 76.75, 19.15, 84.75]
    }
}


@app.get("/api/aoi/search")
@app.get("/api/v1/aoi/search")
def search_area_of_interest(q: str = Query(..., description="Location place name")):
    """
    Simple location search endpoint.
    Returns standardized AOI metadata and coordinates.
    Example: GET /api/aoi/search?q=gudlavalleru
    Response: { "aoi": "gudlavalleru", "display_name": "Gudlavalleru, Andhra Pradesh, India", "center": {"lat": 16.02, "lon": 80.70} }
    """
    cleaned = q.strip().lower()
    for key, entry in AOI_REGISTRY.items():
        if cleaned == key or key in cleaned or cleaned in key:
            return entry
    
    # Dynamic geocoding via copernicus_service for arbitrary global/Indian locations
    disp_name, bbox, center = copernicus_service.geocode_place(cleaned)
    return {
        "aoi": cleaned.replace(" ", "_"),
        "display_name": disp_name,
        "center": center,
        "bbox": bbox
    }


@app.get("/api/scenes")
def get_scenes_catalog(
    aoi: Optional[str] = Query(None, description="Filter by Area of Interest"),
    sensor: Optional[str] = Query(None, description="Filter by Sensor name"),
    date_from: Optional[str] = Query(None, description="Filter from date YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="Filter to date YYYY-MM-DD"),
    max_cloud_cover: Optional[float] = Query(None, description="Max cloud cover percentage"),
):
    """
    Query scene catalog with filtering on AOI, sensor, and date range.
    Returns scenes in standardized schema with thumbnail_url and metadata_url.
    """
    filtered = catalog_service.filter_scenes(
        aoi=aoi,
        sensor=sensor,
        date_from=date_from,
        date_to=date_to,
        max_cloud_cover=max_cloud_cover
    )
    return {
        "scenes": [
            {
                "id": s["id"],
                "aoi": s["aoi"],
                "sensor": s["sensor"],
                "level": s.get("level", "L2A"),
                "date": s["date"],
                "cloud_cover": s.get("cloud_cover", 0.0),
                "thumbnail_url": s.get("thumbnail_url", ""),
                "metadata_url": s.get("metadata_url", f"/api/scenes/{s['id']}")
            }
            for s in filtered
        ]
    }


@app.get("/api/scenes/{scene_id}")
def get_scene_metadata(scene_id: str):
    """Retrieves full metadata for a specific cataloged satellite scene."""
    scene = catalog_service.get_scene_by_id(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene '{scene_id}' not found in catalog.")
    return scene


@app.get("/api/v1/scenes")
def list_catalog_scenes(
    aoi: Optional[str] = Query(None, description="Filter by Area of Interest"),
    sensor: Optional[str] = Query(None, description="Filter by Sensor name"),
    modality: Optional[str] = Query(None, description="Filter by modality"),
    max_cloud_cover: Optional[float] = Query(None, description="Max cloud cover percentage"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
):
    """Discovers satellite scenes matching geographical, temporal, and sensor filters."""
    return catalog_service.filter_scenes(
        aoi=aoi, sensor=sensor, modality=modality, max_cloud_cover=max_cloud_cover,
        start_date=start_date, end_date=end_date
    )


@app.get("/api/v1/scenes/{scene_id}")
def get_catalog_scene(scene_id: str):
    """Retrieves full metadata for a specific cataloged satellite scene."""
    scene = catalog_service.get_scene_by_id(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene '{scene_id}' not found in catalog.")
    return scene


@app.get("/api/copernicus/scenes")
@app.get("/api/v1/copernicus/scenes")
def search_copernicus_scenes(
    aoi_name: Optional[str] = Query("Gudlavalleru", description="Location name or place"),
    bbox: Optional[str] = Query(None, description="Comma-separated bbox [min_lat, min_lon, max_lat, max_lon]"),
    date_from: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    max_cloud: float = Query(30.0, description="Max cloud cover percentage"),
    limit: int = Query(10, description="Max scenes to return")
):
    """
    Automatic scene fetching from Copernicus Data Space Ecosystem.
    Searches Sentinel-2 L2A optical scenes matching location, date, and cloud cover.
    """
    parsed_bbox = None
    if bbox:
        try:
            parsed_bbox = [float(x.strip()) for x in bbox.split(",")]
        except Exception:
            parsed_bbox = None
    return copernicus_service.search_scenes(
        aoi_name=aoi_name,
        bbox=parsed_bbox,
        date_from=date_from,
        date_to=date_to,
        max_cloud=max_cloud,
        limit=limit
    )


@app.get("/api/traces/{trace_id}")
@app.get("/api/v1/traces/{trace_id}")
@app.get("/api/v1/trace/{trace_id}")
def get_audit_trace(trace_id: str):
    """Retrieves an auditable, cryptographically hashed execution trace for post-mission verification."""
    trace = trace_service.get_trace(trace_id)
    if not trace:
        trace = SESSION_TRACES.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Execution trace '{trace_id}' not found.")
    return trace


@app.get("/api/traces")
@app.get("/api/v1/traces")
def list_audit_traces(limit: int = 50):
    """Lists recently executed audit traces for post-analysis review."""
    return trace_service.list_traces(limit=limit)


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_remote_sensing_query(
    query: str = Form(...),
    task_hint: Optional[str] = Form("auto"),
    scenario_id: Optional[str] = Form(None),
    scene_ids: Optional[str] = Form(None),
    analysis_mode: Optional[str] = Form(None),
    session_trace_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Primary agentic remote-sensing query endpoint.
    Accepts user-uploaded satellite image files (GeoTIFF/PNG/JPEG),
    pre-configured demo scenarios, or catalog-indexed scenes (e.g. Gudlavalleru).
    """
    raw_images = []
    filenames = []
    modalities = []
    scenario_meta = {}

    # -------------------------------------------------------------------------
    # CRITICAL BUG FIX (SIH-26167):
    # What s_dir represents:
    #   s_dir stores the Path to a pre-packaged demonstration directory under
    #   settings.DEMO_SCENARIOS_DIR (e.g. scenario_1_flood, scenario_2_urban).
    #
    # Under what conditions s_dir may be unset (None):
    #   1. When querying near-real-time streaming scenes ("scenario_today_near_real_time" or "today").
    #   2. When querying catalog-indexed scenes by ID (e.g. Gudlavalleru "gvl_s2_2025_09_03").
    #   3. When the operator uploads custom satellite GeoTIFF / PNG files directly.
    #
    # In earlier versions, s_dir was only assigned in the `else` branch of scenario_id,
    # causing an UnboundLocalError when checking `if s_dir.exists():` on NRT or catalog scenes.
    # We now explicitly initialize s_dir = None and strictly guard `if s_dir is not None:`.
    # -------------------------------------------------------------------------
    s_dir: Optional[Path] = None

    # Parse target scene ID(s) if provided
    resolved_scene_ids: List[str] = []
    if scene_ids:
        raw_sids = scene_ids.strip()
        if raw_sids.startswith("[") and raw_sids.endswith("]"):
            try:
                resolved_scene_ids = json.loads(raw_sids)
            except Exception:
                resolved_scene_ids = [s.strip().strip('"').strip("'") for s in raw_sids[1:-1].split(",") if s.strip()]
        else:
            resolved_scene_ids = [s.strip() for s in raw_sids.split(",") if s.strip()]
    elif scenario_id:
        if "," in scenario_id:
            resolved_scene_ids = [s.strip() for s in scenario_id.split(",") if s.strip()]
        else:
            resolved_scene_ids = [scenario_id.strip()]

    # 1. Handle scenario or scene ID(s)
    if resolved_scene_ids:
        # Check if all specified IDs correspond to catalog scenes or copernicus scenes
        catalog_scenes = [
            catalog_service.get_scene_by_id(sid) or copernicus_service.get_scene_by_id(sid)
            for sid in resolved_scene_ids
        ]
        if all(cs is not None for cs in catalog_scenes):
            for cs in catalog_scenes:
                rel_path = cs.get("path_rgb") or cs.get("file_path") or cs.get("path_all_bands")
                target_fpath = None
                if rel_path:
                    p = Path(rel_path)
                    if p.is_absolute() and p.exists():
                        target_fpath = p
                    else:
                        for cand in [settings.ROOT_DIR / rel_path, settings.DATA_DIR / rel_path, Path(rel_path)]:
                            if cand.exists():
                                target_fpath = cand
                                break
                if not target_fpath or not target_fpath.exists():
                    thumb_rel = cs.get("thumbnail") or cs.get("preview_path") or cs.get("thumbnail_url") or ""
                    if thumb_rel:
                        for cand_th in [
                            settings.ROOT_DIR / thumb_rel.lstrip("/\\"),
                            settings.STATIC_DIR / Path(thumb_rel).name,
                            settings.STATIC_DIR / "thumbs" / Path(thumb_rel).name
                        ]:
                            if cand_th.exists():
                                target_fpath = cand_th
                                break

                if not target_fpath or not target_fpath.exists():
                    fallback_cands = [
                        settings.DATA_DIR / "andhra_pradesh" / "ap_state_overview" / "s2_2026_09_03" / "rgb_512.tif",
                        settings.DATA_DIR / "latest" / "latest_scene.tif",
                        settings.DEMO_SCENARIOS_DIR / "scenario_1_flood" / "image1.tif"
                    ]
                    for fc in fallback_cands:
                        if fc.exists():
                            target_fpath = fc
                            break
                
                if not target_fpath or not target_fpath.exists():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Satellite raster data file for scene '{cs.get('id') or cs.get('scene_id')}' not found on disk."
                    )
                
                arr, _ = load_image_from_path(target_fpath)
                raw_images.append(arr)
                filenames.append(target_fpath.name)
                modalities.append(detect_modality_heuristics(target_fpath.name, arr.shape[2] if arr.ndim == 3 else 1, arr))

            scenario_meta = {
                "sensor": catalog_scenes[0].get("sensor", "Sentinel-2"),
                "area": catalog_scenes[0].get("aoi", "Copernicus Target AOI"),
                "resolution": f"{catalog_scenes[0].get('resolution_m', 10)} m GSD",
                "crs": catalog_scenes[0].get("crs", "EPSG:4326"),
                "real_data_source": catalog_scenes[0].get("real_data_source") or catalog_scenes[0].get("source") or "Copernicus Sentinel-2 L2A BOA Reflectance"
            }

            if len(raw_images) >= 2 and (analysis_mode == "change" or task_hint == "auto"):
                task_hint = "change_detection"
            elif len(raw_images) == 1 and analysis_mode == "single":
                if task_hint == "auto":
                    task_hint = "single_image_vqa"

        elif len(resolved_scene_ids) == 1 and resolved_scene_ids[0] in ("scenario_today_near_real_time", "today"):
            scenario = catalog_service.get_todays_scenario()
            scenario_meta = scenario.model_dump()
            latest_tif = settings.DATA_DIR / "latest" / "latest_scene.tif"
            latest_png = settings.DATA_DIR / "latest" / "latest_scene.png"
            target_fpath = latest_tif if latest_tif.exists() else (latest_png if latest_png.exists() else None)
            if target_fpath and target_fpath.exists():
                arr, _ = load_image_from_path(target_fpath)
                raw_images.append(arr)
                filenames.append(target_fpath.name)
                modalities.append(detect_modality_heuristics(target_fpath.name, arr.shape[2] if arr.ndim == 3 else 1, arr))
            else:
                fallback_path = settings.DEMO_SCENARIOS_DIR / "scenario_1_flood" / "image1.tif"
                if not fallback_path.exists():
                    fallback_path = settings.DEMO_SCENARIOS_DIR / "scenario_1_flood" / "image1.png"
                arr, _ = load_image_from_path(fallback_path)
                raw_images.append(arr)
                filenames.append(fallback_path.name)
                modalities.append("optical_multispectral")
        else:
            # Demonstration scenarios (scenario_1_flood, scenario_2_urban, etc.)
            target_scenario_id = resolved_scene_ids[0]
            scenarios = get_all_scenarios()
            scenario = next((s for s in scenarios if s.id == target_scenario_id), None)
            if not scenario:
                raise HTTPException(status_code=404, detail=f"Scenario or scene '{target_scenario_id}' not found.")
            
            scenario_meta = scenario.model_dump()
            demo_pkg_cand = settings.ROOT_DIR / "backend" / "demo_data" / target_scenario_id
            if demo_pkg_cand.exists():
                s_dir = demo_pkg_cand
            else:
                s_dir = settings.DEMO_SCENARIOS_DIR / target_scenario_id

        # Safely read from s_dir only if s_dir was assigned and exists
        if s_dir is not None:
            if s_dir.exists():
                if (s_dir / "pre.tif").exists() and (s_dir / "post.tif").exists():
                    load_targets = [s_dir / "pre.tif", s_dir / "post.tif"]
                elif (s_dir / "pre.png").exists() and (s_dir / "post.png").exists():
                    load_targets = [s_dir / "pre.png", s_dir / "post.png"]
                else:
                    tif_files = sorted(s_dir.glob("*.tif"))
                    png_files = sorted(s_dir.glob("*.png"))
                    load_targets = tif_files if tif_files else png_files
                for fpath in load_targets:
                    arr, _ = load_image_from_path(fpath)
                    raw_images.append(arr)
                    filenames.append(fpath.name)
                    modalities.append(detect_modality_heuristics(fpath.name, arr.shape[2] if arr.ndim == 3 else 1, arr))
            else:
                for rel_path in scenario.image_paths:
                    fname = os.path.basename(rel_path)
                    disk_path = settings.SAMPLES_DIR / fname
                    if not disk_path.exists():
                        raise HTTPException(status_code=404, detail=f"Sample file missing: {fname}")
                    with open(disk_path, "rb") as f:
                        content = f.read()
                    arr, _ = load_image_from_bytes(content, filename=fname)
                    raw_images.append(arr)
                    filenames.append(fname)
                    modalities.append(detect_modality_heuristics(fname, arr.shape[2] if arr.ndim == 3 else 1, arr))

    # 2. Handle multi-query session reuse
    elif session_trace_id and session_trace_id in SESSION_TRACES:
        prev = SESSION_TRACES[session_trace_id]
        raw_images.append(prev["base_image"])
        filenames.append("session_base.png")
        modalities.append("optical_multispectral")
        if prev.get("comparison_image") is not None:
            raw_images.append(prev["comparison_image"])
            filenames.append("session_comp.png")
            modalities.append("optical_multispectral")
        scenario_meta = {
            "sensor": prev.get("input_summary", {}).get("sensor", "Sentinel-2 L2A MSI"),
            "area": prev.get("input_summary", {}).get("area", "Multi-Query Session Active Corridor"),
            "crs": prev.get("input_summary", {}).get("crs", "EPSG:4326"),
            "real_data_source": prev.get("input_summary", {}).get("data_source", "Active Session Cache")
        }

    # 3. Handle user custom upload flow
    else:
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="Must upload 1 or 2 satellite images (GeoTIFF / PNG), select a pre-configured scenario/scene, or provide an active session_trace_id."
            )
        validated_files = await validate_upload_files(files)
        for content, fname in validated_files:
            arr, _ = load_image_from_bytes(content, filename=fname)
            raw_images.append(arr)
            filenames.append(fname)
            modalities.append(detect_modality_heuristics(fname, arr.shape[2] if arr.ndim == 3 else 1, arr))

        scenario_meta = {
            "sensor": "User Uploaded Satellite Sensor",
            "real_data_source": "User Uploaded Satellite Scene",
            "area": "Operator Region of Interest",
            "crs": "EPSG:4326"
        }

    # Ensure valid imagery was resolved
    if not raw_images or len(raw_images) == 0:
        raise HTTPException(
            status_code=400,
            detail="No valid satellite image data could be loaded for processing."
        )

    # Execute Agent Controller with full real satellite metadata
    response = controller.execute(
        query=query,
        images=raw_images,
        modalities=modalities,
        image_names=filenames,
        task_hint=task_hint,
        scenario_meta=scenario_meta
    )

    # Save session trace & images for PDF report generation
    trace_id = response.execution_trace.trace_id
    comp_image = raw_images[1] if len(raw_images) > 1 else None
    SESSION_TRACES[trace_id] = {
        "query": query,
        "detected_task": response.detected_task,
        "analysis_result": response.result.model_dump(),
        "execution_trace": response.execution_trace.model_dump(),
        "input_summary": response.input_summary.model_dump(),
        "base_image": raw_images[0],
        "comparison_image": comp_image,
        "evidence_overlay_b64": response.result.visual_evidence.overlay_base64 if response.result.visual_evidence else None
    }

    # Persist verifiable output package to disk under outputs/{trace_id}
    try:
        out_dir = settings.ROOT_DIR / "outputs" / trace_id
        out_dir.mkdir(parents=True, exist_ok=True)
        if response.result.visual_evidence and response.result.visual_evidence.overlay_base64:
            import base64
            ov_data = response.result.visual_evidence.overlay_base64.split(",")[-1]
            with open(out_dir / "change_overlay.png", "wb") as f:
                f.write(base64.b64decode(ov_data))
        with open(out_dir / "trace.json", "w") as f:
            json.dump(response.execution_trace.model_dump(), f, indent=2)
        if response.result.visual_evidence and response.result.visual_evidence.metric_summary:
            with open(out_dir / "statistics.json", "w") as f:
                json.dump(response.result.visual_evidence.metric_summary, f, indent=2)
    except Exception as err:
        print(f"Warning: Failed to persist output package for {trace_id}: {err}")

    return response


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_remote_sensing_query_alias(
    query: str = Form(...),
    task_hint: Optional[str] = Form("auto"),
    scenario_id: Optional[str] = Form(None),
    scene_ids: Optional[str] = Form(None),
    analysis_mode: Optional[str] = Form(None),
    session_trace_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """Alias for /api/v1/analyze supporting all parameter combinations."""
    return await analyze_remote_sensing_query(
        query=query,
        task_hint=task_hint,
        scenario_id=scenario_id,
        scene_ids=scene_ids,
        analysis_mode=analysis_mode,
        session_trace_id=session_trace_id,
        files=files
    )


@app.get("/api/v1/report/pdf")
def download_pdf_report(trace_id: str = Query(...)):
    """
    Generates and returns an official PDF mission intelligence report for a given execution trace.
    """
    session = SESSION_TRACES.get(trace_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"No execution record found for trace '{trace_id}'.")

    pdf_filename = f"SatQuery_MissionReport_{trace_id}.pdf"
    pdf_path = settings.REPORTS_DIR / pdf_filename

    # Encode base image
    base_buf = io.BytesIO()
    from PIL import Image
    Image.fromarray(session["base_image"]).save(base_buf, format="PNG")
    base_bytes = base_buf.getvalue()

    # Encode comparison image if available (e.g. for bi-temporal 2025 vs 2026)
    comp_bytes = None
    if session.get("comparison_image") is not None:
        comp_buf = io.BytesIO()
        Image.fromarray(session["comparison_image"]).save(comp_buf, format="PNG")
        comp_bytes = comp_buf.getvalue()

    # Decode evidence overlay
    evidence_bytes = None
    if session.get("evidence_overlay_b64"):
        import base64
        b64_data = session["evidence_overlay_b64"].split(",")[-1]
        evidence_bytes = base64.b64decode(b64_data)

    generate_mission_pdf_report(
        output_path=pdf_path,
        query=session["query"],
        detected_task=session["detected_task"],
        analysis_result=session["analysis_result"],
        execution_trace=session["execution_trace"],
        input_summary=session["input_summary"],
        base_image_bytes=base_bytes,
        comparison_image_bytes=comp_bytes,
        evidence_image_bytes=evidence_bytes
    )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename
    )


@app.get("/", response_class=HTMLResponse)
def serve_mission_control_ui():
    """
    Serves the integrated zero-setup Mission Control Web Interface.
    Full-featured: Multi-panel viewer, layer toggles, comparison slider, live trace drawer, and instant scenarios.
    """
    return HTMLResponse(content=MISSION_CONTROL_HTML)
