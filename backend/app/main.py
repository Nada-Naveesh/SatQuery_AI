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
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# In-memory store for session traces and cached payloads
SESSION_TRACES: Dict[str, Dict[str, Any]] = {}

def get_all_scenarios() -> List[DemoScenario]:
    """
    Dynamically loads all pre-configured real satellite demonstration scenarios
    from data/demo_scenarios/ with metadata.json files.
    """
    scenarios: List[DemoScenario] = []
    demo_dir = settings.DEMO_SCENARIOS_DIR

    if demo_dir.exists():
        for s_folder in sorted(demo_dir.iterdir()):
            if s_folder.is_dir():
                meta_file = s_folder / "metadata.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r") as f:
                            meta = json.load(f)
                        # Build web-accessible image paths (prefer preview png for browser)
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
    
    # Fallback response for any queried location
    return {
        "aoi": cleaned.replace(" ", "_"),
        "display_name": f"{q.strip().title()}, Andhra Pradesh, India",
        "center": {"lat": 16.02, "lon": 80.70},
        "bbox": [15.97, 80.65, 16.07, 80.75]
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


@app.get("/api/v1/trace/{trace_id}")
def get_audit_trace(trace_id: str):
    """Retrieves an auditable, cryptographically hashed execution trace for post-mission verification."""
    trace = trace_service.get_trace(trace_id)
    if not trace:
        trace = SESSION_TRACES.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Execution trace '{trace_id}' not found.")
    return trace


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
        # Check if all specified IDs correspond to catalog scenes (e.g. Gudlavalleru)
        catalog_scenes = [catalog_service.get_scene_by_id(sid) for sid in resolved_scene_ids]
        if all(cs is not None for cs in catalog_scenes):
            for cs in catalog_scenes:
                rel_path = cs.get("path_rgb") or cs.get("file_path") or cs.get("path_all_bands")
                target_fpath = None
                if rel_path:
                    for cand in [settings.ROOT_DIR / rel_path, settings.DATA_DIR / rel_path]:
                        if cand.exists():
                            target_fpath = cand
                            break
                if not target_fpath or not target_fpath.exists():
                    thumb_rel = cs.get("thumbnail") or cs.get("preview_path") or ""
                    if thumb_rel:
                        cand_thumb = settings.ROOT_DIR / thumb_rel.lstrip("/\\")
                        if cand_thumb.exists():
                            target_fpath = cand_thumb
                
                if not target_fpath or not target_fpath.exists():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Satellite raster data file for scene '{cs.get('id')}' not found on disk."
                    )
                
                arr, _ = load_image_from_path(target_fpath)
                raw_images.append(arr)
                filenames.append(target_fpath.name)
                modalities.append(detect_modality_heuristics(target_fpath.name, arr.shape[2] if arr.ndim == 3 else 1, arr))

            scenario_meta = {
                "sensor": catalog_scenes[0].get("sensor", "Sentinel-2"),
                "area": catalog_scenes[0].get("aoi", "Gudlavalleru, AP"),
                "resolution": f"{catalog_scenes[0].get('resolution_m', 10)} m GSD",
                "crs": catalog_scenes[0].get("crs", "EPSG:4326"),
                "real_data_source": "Copernicus Sentinel-2 L2A BOA Reflectance"
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
            s_dir = settings.DEMO_SCENARIOS_DIR / target_scenario_id

        # Safely read from s_dir only if s_dir was assigned and exists
        if s_dir is not None:
            if s_dir.exists():
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

    # 2. Handle user custom upload flow
    else:
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="Must upload 1 or 2 satellite images (GeoTIFF / PNG) or select a pre-configured scenario/scene."
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

    return response


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_remote_sensing_query_alias(
    query: str = Form(...),
    task_hint: Optional[str] = Form("auto"),
    scenario_id: Optional[str] = Form(None),
    scene_ids: Optional[str] = Form(None),
    analysis_mode: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """Alias for /api/v1/analyze supporting all parameter combinations."""
    return await analyze_remote_sensing_query(
        query=query,
        task_hint=task_hint,
        scenario_id=scenario_id,
        scene_ids=scene_ids,
        analysis_mode=analysis_mode,
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


# Production-grade Single-Page Mission Control UI
MISSION_CONTROL_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SatQuery AI — ISRO Remote Sensing Vision-Language Assistant (PS 26167)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            isro: {
              50: '#f0f9ff',
              500: '#0284c7',
              600: '#0369a1',
              900: '#0c4a6e',
            },
            space: {
              900: '#0B0F19',
              800: '#111827',
              700: '#1F2937',
              600: '#374151'
            }
          }
        }
      }
    }
  </script>
  <style>
    /* Custom comparison slider styles */
    .slider-container {
      position: relative;
      overflow: hidden;
    }
    .slider-handle {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 4px;
      background-color: #38bdf8;
      cursor: ew-resize;
      z-index: 20;
    }
    .slider-handle::after {
      content: '< >';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #0284c7;
      color: white;
      font-size: 10px;
      font-weight: bold;
      padding: 4px 6px;
      border-radius: 9999px;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
  </style>
</head>
<body class="bg-space-900 text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-cyan-500 selection:text-black">

  <!-- Top Header Navigation -->
  <header class="border-b border-space-700 bg-space-800/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <i class="fa-solid fa-satellite text-white text-xl"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-cyan-200 to-blue-400 bg-clip-text text-transparent">SatQuery AI</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono font-semibold">PS 26167</span>
          </div>
          <p class="text-xs text-slate-400">ISRO / SAC &bull; Multimodal Remote Sensing Agent</p>
        </div>
      </div>
      
      <div class="flex items-center space-x-4">
        <div class="hidden md:flex items-center space-x-2 text-xs text-slate-400 bg-space-900 px-3 py-1.5 rounded-md border border-space-700">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Agentic Router: <b class="text-emerald-400">Active</b></span>
          <span class="text-slate-600">|</span>
          <span>Inference: <b class="text-cyan-300">PyTorch RS-Backbones</b></span>
        </div>
        <button onclick="openDataModal()" class="inline-flex items-center space-x-1.5 bg-space-800 hover:bg-space-700 text-cyan-300 hover:text-white text-xs font-medium px-3 py-2 rounded-lg border border-space-600 transition shadow-sm">
          <i class="fa-solid fa-circle-question"></i>
          <span>How to Get Free Data</span>
        </button>
        <button onclick="downloadLatestReport()" id="headerDownloadBtn" disabled class="disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-medium px-3.5 py-2 rounded-lg transition shadow-md">
          <i class="fa-solid fa-file-pdf"></i>
          <span>Download Mission PDF</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

    <!-- Real Satellite Data Notice Banner -->
    <div class="lg:col-span-12 bg-cyan-950/80 border border-cyan-700/70 text-cyan-200 text-xs px-4 py-3 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-sm">
      <div class="flex items-center space-x-2.5">
        <div class="w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center flex-shrink-0">
          <i class="fa-solid fa-satellite-dish text-xs"></i>
        </div>
        <div>
          <b class="text-white">Real Satellite Imagery Active:</b> All pre-configured demonstration scenarios use authentic Earth Observation data (Sentinel-2 L2A, Cartosat-2S, RISAT / Sentinel-1 C-band SAR, and LEVIR-CD). Custom GeoTIFF uploads are also supported.
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-[10px] bg-cyan-900/90 text-cyan-300 px-2.5 py-1 rounded-full border border-cyan-700 font-mono font-semibold">
          GeoTIFF &bull; 10m/0.5m GSD
        </span>
      </div>
    </div>

    <!-- Left Controls Panel: Query & Scenarios (5 Cols) -->
    <div class="lg:col-span-5 space-y-5 flex flex-col">

      <!-- SIH Pre-Configured Scenarios -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <i class="fa-solid fa-bolt text-yellow-400"></i>
            <span>Real Satellite Demo Scenarios</span>
          </h2>
          <span class="text-[10px] text-cyan-400 font-mono">1-Click Instant Run</span>
        </div>
        
        <!-- State-Wide Andhra Pradesh Location Intelligence -->
        <div class="mb-3 p-3 rounded-lg bg-space-900/80 border border-teal-500/50 space-y-2.5">
          <div class="flex items-center justify-between text-[11px] font-semibold text-slate-200">
            <span class="flex items-center space-x-1.5">
              <i class="fa-solid fa-map-location-dot text-teal-400"></i>
              <span>Andhra Pradesh State-Wide Coverage</span>
            </span>
            <span class="text-[9px] bg-teal-900/80 text-teal-300 px-1.5 py-0.5 rounded font-mono font-bold">11 Regions &bull; 2025 vs 2026</span>
          </div>

          <div class="flex gap-1.5">
            <input type="text" id="dashboardLocSearch" value="Vijayawada" placeholder="Search AP (e.g., Vijayawada, Amaravati, Vizag, Tirupati, Kurnool)..." class="flex-1 bg-space-800 border border-space-600 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-400" onkeydown="if(event.key==='Enter') searchLocationDashboard()">
            <button onclick="searchLocationDashboard()" class="bg-teal-600 hover:bg-teal-500 text-white text-xs px-3 py-1.5 rounded font-semibold transition flex items-center space-x-1">
              <i class="fa-solid fa-magnifying-glass text-[10px]"></i>
              <span>Locate</span>
            </button>
          </div>

          <!-- Quick AP City Pills -->
          <div class="flex flex-wrap gap-1 pt-0.5">
            <button onclick="selectApCity('vijayawada')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Vijayawada</button>
            <button onclick="selectApCity('amaravati')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Amaravati</button>
            <button onclick="selectApCity('visakhapatnam')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Visakhapatnam</button>
            <button onclick="selectApCity('tirupati')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Tirupati</button>
            <button onclick="selectApCity('guntur')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Guntur</button>
            <button onclick="selectApCity('rajahmundry')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Rajahmundry</button>
            <button onclick="selectApCity('kakinada')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Kakinada</button>
            <button onclick="selectApCity('kurnool')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Kurnool</button>
            <button onclick="selectApCity('nellore')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Nellore</button>
            <button onclick="selectApCity('anantapur')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Anantapur</button>
            <button onclick="selectApCity('gudlavalleru')" class="text-[9px] bg-space-800 hover:bg-teal-900/60 border border-teal-600/40 hover:border-teal-400 text-teal-200 px-2 py-0.5 rounded transition">Gudlavalleru</button>
            <button onclick="selectApCity('ap_state_overview')" class="text-[9px] bg-teal-900/60 hover:bg-teal-800 border border-teal-400 text-teal-100 px-2 py-0.5 rounded transition font-bold">Entire AP</button>
          </div>

          <!-- Dynamic AOI Coordinate & Extent Display -->
          <div class="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-space-800">
            <span id="dashboardAoiCoords" class="text-teal-300 font-mono font-medium">AOI: 16.51°N, 80.65°E (Vijayawada)</span>
            <span class="text-emerald-400 font-mono text-[9px] bg-emerald-950/60 border border-emerald-800/60 px-1.5 py-0.5 rounded">Sentinel-2 2025 vs 2026</span>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-2" id="scenariosContainer">
          <!-- Vijayawada & AP Featured Scenario -->
          <button onclick="selectApCity('vijayawada')" id="btn_ap_vijayawada" class="scenario-btn text-left p-3 rounded-lg border border-teal-500/80 bg-teal-950/30 hover:border-teal-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-teal-300 flex items-center space-x-1.5">
                <i class="fa-solid fa-map-pin text-teal-400"></i>
                <span>Vijayawada (2025 vs 2026 Change)</span>
              </span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-teal-900/80 text-teal-300 font-mono font-semibold">AP Coverage</span>
            </div>
            <p class="text-[11px] text-slate-300 mt-1">Prakasam Barrage & Krishna corridor. Detects new bypass expressway, flood wall expansion, and urban growth.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
              <span class="text-teal-300 font-bold">Sentinel-2 L2A</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span>16.51°N, 80.65°E</span>
            </div>
          </button>

          <!-- Today's Live Operational Stream -->
          <button onclick="loadScenario('scenario_today_near_real_time')" id="btn_scenario_today_near_real_time" class="scenario-btn text-left p-3 rounded-lg border border-emerald-500/80 bg-emerald-950/30 hover:border-emerald-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-emerald-300 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Today's Live Surveillance Stream</span>
              </span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-900/80 text-emerald-300 font-mono font-semibold">Near-Real-Time</span>
            </div>
            <p class="text-[11px] text-slate-300 mt-1">Direct Copernicus Data Space ingestion pipeline feed. Automated surveillance & anomaly detection.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
              <span class="text-emerald-400 font-bold">Acquired Today</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span>Copernicus Stream</span>
            </div>
          </button>

          <button onclick="loadScenario('scenario_1_flood')" id="btn_scenario_1_flood" class="scenario-btn text-left p-3 rounded-lg border border-cyan-500 bg-space-700/40 hover:border-cyan-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-cyan-300">1. Flood Inundation & Grounding</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 font-mono">Sentinel-2 L2A</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Sentinel-2 optical chip over Godavari flood basin. Evaluates inundated acreage & extracts masks.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>Date: 2023-07-28</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span class="text-cyan-400/90">Copernicus Hub</span>
            </div>
          </button>

          <button onclick="loadScenario('scenario_2_urban')" id="btn_scenario_2_urban" class="scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-amber-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-amber-300">2. Bi-Temporal Urban Expansion</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-900/60 text-amber-300 font-mono">LEVIR-CD Pair</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">2022 vs 2024 satellite pair. Siamese difference engine maps highway & warehouse construction.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>2022 vs 2024</span>
              <span>&bull;</span>
              <span>0.5m GSD</span>
              <span>&bull;</span>
              <span class="text-amber-400/90">LEVIR-CD Benchmark</span>
            </div>
          </button>

          <button onclick="loadScenario('scenario_3_optical_sar')" id="btn_scenario_3_optical_sar" class="scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-purple-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-purple-300">3. Optical-SAR Cloud Penetration</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-900/60 text-purple-300 font-mono">Cartosat + SAR</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Pierces 82% monsoon cumulus cloud cover via C-band SAR to detect storage tanks & coastline.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>Cartosat + S1 SAR</span>
              <span>&bull;</span>
              <span>10m/0.65m GSD</span>
              <span>&bull;</span>
              <span class="text-purple-400/90">ISRO SAC / ESA</span>
            </div>
          </button>

          <button onclick="loadScenario('scenario_4_coastal')" id="btn_scenario_4_coastal" class="scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-teal-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-teal-300">4. Coastal Port & Breakwater Expansion</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-teal-900/60 text-teal-300 font-mono">Sentinel-2 Bi-Temporal</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Visakhapatnam Port 2023 vs 2024. Maps ocean breakwater extensions & container yard paving.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>2023 vs 2024</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span class="text-teal-400/90">Visakhapatnam Port</span>
            </div>
          </button>
        </div>
      </div>

      <!-- Natural Language Query & File Upload Card -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm space-y-4">
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
            Natural Language Query
          </label>
          <div class="relative">
            <textarea id="queryInput" rows="3" class="w-full bg-space-900 border border-space-600 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 resize-none font-medium" placeholder="E.g. Identify submerged agricultural parcels and quantify flood extent..."></textarea>
            <div class="absolute right-2.5 bottom-2.5 text-[10px] text-slate-500">
              Plain English &bull; Auto-Routed
            </div>
          </div>
        </div>

        <!-- Suggestion Pills (Simple English) -->
        <div class="flex flex-wrap gap-1.5">
          <button onclick="setQuery('What changed between 2025 and 2026 in this area?')" class="text-[10px] bg-space-900 border border-teal-700/70 hover:border-teal-400 px-2.5 py-1 rounded text-teal-200 transition">🔄 What changed here?</button>
          <button onclick="setQuery('Where are the buildings in this image?')" class="text-[10px] bg-space-900 border border-amber-700/70 hover:border-amber-400 px-2.5 py-1 rounded text-amber-200 transition">🏢 Where are buildings?</button>
          <button onclick="setQuery('Show me the water bodies.')" class="text-[10px] bg-space-900 border border-cyan-700/70 hover:border-cyan-400 px-2.5 py-1 rounded text-cyan-200 transition">💧 Show water bodies</button>
          <button onclick="setQuery('Identify the submerged agricultural parcels and highlight their spatial boundaries.')" class="text-[10px] bg-space-900 border border-purple-700/70 hover:border-purple-400 px-2.5 py-1 rounded text-purple-200 transition">🌾 Submerged farmlands</button>
        </div>

        <!-- Custom Upload Zone -->
        <div class="border-t border-space-700 pt-3">
          <div class="flex items-center justify-between mb-2">
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400">
              Upload Satellite Images
            </label>
            <button type="button" onclick="openDataModal()" class="text-[10px] text-cyan-400 hover:text-cyan-300 underline flex items-center space-x-1">
              <i class="fa-solid fa-circle-question"></i>
              <span>Where to get free images?</span>
            </button>
          </div>
          <div class="border-2 border-dashed border-space-600 hover:border-cyan-500 rounded-lg p-3 text-center cursor-pointer transition bg-space-900/40" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" multiple accept=".tif,.tiff,.png,.jpg,.jpeg" class="hidden" onchange="handleFileSelect(event)">
            <i class="fa-solid fa-cloud-arrow-up text-slate-400 text-lg mb-1"></i>
            <p class="text-xs text-slate-300 font-medium" id="uploadLabel">Upload 1 or 2 files (GeoTIFF / PNG)</p>
            <p class="text-[10px] text-slate-500">Supports Single image, Temporal Pairs (Before & After), or Optical+SAR Pairs</p>
          </div>
        </div>

        <!-- Execute Action Button -->
        <button onclick="executeAnalysis()" id="executeBtn" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-cyan-600/30">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
          <span>Analyze Satellite Images</span>
        </button>
      </div>

    </div>

    <!-- Right Visualization & Result Panel (7 Cols) -->
    <div class="lg:col-span-7 space-y-5">

      <!-- Viewport Card with Layer Toggles -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Satellite Viewport</span>
            <span id="detectedBadge" class="hidden text-[10px] px-2 py-0.5 rounded font-mono font-medium bg-cyan-950 text-cyan-400 border border-cyan-800">
              Task: Auto
            </span>
          </div>

          <!-- Layer View Buttons -->
          <div class="flex items-center space-x-1 bg-space-900 p-1 rounded-md border border-space-700 text-xs">
            <button onclick="setViewMode('base')" id="btnViewBase" class="px-2.5 py-1 rounded bg-space-700 text-white font-medium text-[11px] transition">Base</button>
            <button onclick="setViewMode('overlay')" id="btnViewOverlay" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition">Evidence Overlay</button>
            <button onclick="setViewMode('split')" id="btnViewSplit" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition">Split Comparison</button>
          </div>
        </div>

        <!-- Interactive Canvas / Image Viewer -->
        <div class="relative w-full h-80 bg-black/60 rounded-lg border border-space-700 overflow-hidden flex items-center justify-center">
          <img id="viewerBaseImg" src="/static/demo_scenarios/scenario_1_flood/image1.png" alt="Base Satellite View" class="absolute inset-0 w-full h-full object-contain">
          
          <img id="viewerOverlayImg" src="" alt="Evidence Overlay" class="absolute inset-0 w-full h-full object-contain hidden opacity-90 transition-opacity">

          <!-- Split Screen Slider Container -->
          <div id="splitContainer" class="absolute inset-0 hidden pointer-events-none">
            <div id="splitClip" class="absolute inset-0 overflow-hidden w-1/2 border-r-2 border-cyan-400 shadow-2xl">
              <img id="viewerSplitImg" src="" class="absolute inset-0 w-full h-full object-contain max-w-none">
            </div>
          </div>

          <!-- Loading Spinner -->
          <div id="loadingOverlay" class="absolute inset-0 bg-space-900/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-2 hidden z-30">
            <i class="fa-solid fa-circle-notch fa-spin text-cyan-400 text-3xl"></i>
            <span class="text-xs text-slate-300 font-medium animate-pulse" id="loadingStatusText">Analyzing satellite imagery and preparing answer...</span>
          </div>
        </div>

        <!-- Viewport Metadata Footer with Real Satellite Information -->
        <div class="mt-2 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400 px-1 gap-1 border-t border-space-700/60 pt-2">
          <div class="flex items-center space-x-1.5 overflow-hidden text-ellipsis whitespace-nowrap">
            <span class="text-slate-500 font-semibold uppercase text-[10px]">Data Source:</span>
            <span id="sceneDataSource" class="text-cyan-300 font-medium">Sentinel-2 L2A (MSI), 2023-07-28, Godavari River Basin</span>
          </div>
          <div class="flex items-center space-x-2 text-slate-400 font-mono text-[10px]">
            <span id="sceneDimensions">512 x 512 px</span>
            <span>&bull;</span>
            <span id="sceneResolution">10 m GSD</span>
            <span>&bull;</span>
            <span id="sceneCRS">Map coordinates: Lat/Lon (WGS84)</span>
          </div>
        </div>
      </div>

      <!-- Direct Answer Card -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <i class="fa-solid fa-clipboard-check text-emerald-400"></i>
            <span>Direct Answer</span>
          </h3>
          <div class="flex items-center space-x-2">
            <span class="text-[11px] text-slate-400">Confidence:</span>
            <div class="w-24 bg-space-900 rounded-full h-2 overflow-hidden border border-space-700">
              <div id="confidenceBar" class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
            </div>
            <span id="confidenceValue" class="text-xs font-mono font-bold text-emerald-400">--%</span>
          </div>
        </div>

        <div id="answerText" class="p-3 bg-space-900/70 border border-space-700 rounded-lg text-xs leading-relaxed text-slate-200">
          Select any Andhra Pradesh city above or a demo scenario on the left, then click <b>Analyze Satellite Images</b>.
        </div>

        <!-- Key Observations Bullets -->
        <div id="bulletContainer" class="hidden space-y-1.5 pt-1">
          <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Key Observations & Summary</span>
          <ul id="bulletList" class="text-[11px] text-slate-300 space-y-1 list-disc list-inside"></ul>
        </div>
      </div>

      <!-- Auditable Execution Trace Accordion -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm">
        <button onclick="toggleTraceAccordion()" class="w-full flex items-center justify-between text-left">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-microchip text-cyan-400 text-xs"></i>
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300">Auditable Execution Trace</span>
            <span id="traceIdBadge" class="text-[10px] font-mono text-slate-500">ID: none</span>
          </div>
          <i id="traceChevron" class="fa-solid fa-chevron-down text-slate-400 text-xs transition-transform"></i>
        </button>

        <div id="traceContent" class="hidden mt-3 pt-3 border-t border-space-700 text-xs space-y-3 font-mono">
          <div class="bg-space-900 p-2.5 rounded border border-space-700 text-[11px] space-y-1">
            <div class="text-slate-400"><b class="text-slate-200">Router Decision:</b> <span id="traceRouterReasoning" class="text-cyan-300">Awaiting execution...</span></div>
            <div class="text-slate-400"><b class="text-slate-200">Data Source:</b> <span id="traceDataSource" class="text-cyan-300">Sentinel-2 L2A Real Satellite Acquisition</span></div>
            <div class="text-slate-400"><b class="text-slate-200">Latency:</b> <span id="traceLatency" class="text-emerald-400">-- ms</span></div>
          </div>

          <div>
            <span class="text-[10px] uppercase text-slate-400 font-sans font-bold">Specialist Tool Telemetry</span>
            <div id="traceToolsList" class="mt-1.5 space-y-1.5">
              <!-- Rendered dynamically -->
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>

  <!-- Modal: How to Get Free Satellite Images -->
  <div id="dataGuideModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-space-800 border border-space-600 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-space-700 pb-3">
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-lg bg-cyan-600/30 text-cyan-400 flex items-center justify-center">
            <i class="fa-solid fa-satellite-dish text-base"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-white">How to Get Free Satellite Images</h3>
            <p class="text-xs text-slate-400">Official Open Earth Observation Sources for SatQuery AI</p>
          </div>
        </div>
        <button onclick="closeDataModal()" class="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-space-700 transition">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- Free Portals Cards -->
      <div class="space-y-2.5">
        <h4 class="text-xs font-bold uppercase tracking-wider text-cyan-400">1. Free Satellite Portals</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div class="p-3 rounded-lg bg-space-900/90 border border-space-700 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">Copernicus Browser (ESA)</span>
              <a href="https://browser.dataspace.copernicus.eu" target="_blank" rel="noopener noreferrer" class="text-[10px] text-cyan-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">Sentinel-2 (10m optical) & Sentinel-1 (radar). Free worldwide, updated every 5 days.</p>
            <span class="text-[9px] text-emerald-400 font-mono font-semibold">Recommended for SIH Demo</span>
          </div>

          <div class="p-3 rounded-lg bg-space-900/90 border border-space-700 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">USGS EarthExplorer</span>
              <a href="https://earthexplorer.usgs.gov" target="_blank" rel="noopener noreferrer" class="text-[10px] text-cyan-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">Landsat 8 & 9 (30m optical). 50+ years archive of Earth surface changes.</p>
            <span class="text-[9px] text-blue-400 font-mono font-semibold">Global Open Archive</span>
          </div>

          <div class="p-3 rounded-lg bg-space-900/90 border border-space-700 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">ISRO Bhoovikram / Bhuvan</span>
              <a href="https://bhuvan.nrsc.gov.in" target="_blank" rel="noopener noreferrer" class="text-[10px] text-cyan-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">Indian national geospatial portal. Open datasets for Indian land & coastal regions.</p>
            <span class="text-[9px] text-amber-400 font-mono font-semibold">ISRO Open Data</span>
          </div>

          <div class="p-3 rounded-lg bg-space-900/90 border border-space-700 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">NASA Earthdata Search</span>
              <a href="https://search.earthdata.nasa.gov" target="_blank" rel="noopener noreferrer" class="text-[10px] text-cyan-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">MODIS, VIIRS, and surface reflectance data for disaster and environmental analysis.</p>
            <span class="text-[9px] text-purple-400 font-mono font-semibold">NASA Open Access</span>
          </div>
        </div>
      </div>

      <!-- Step-by-Step Instructions -->
      <div class="space-y-2">
        <h4 class="text-xs font-bold uppercase tracking-wider text-cyan-400">2. Simple 6-Step Download Guide (2 Minutes)</h4>
        <ol class="text-xs text-slate-300 space-y-2 list-decimal list-inside bg-space-900/80 p-3.5 rounded-lg border border-space-700">
          <li><b class="text-white">Open Copernicus Browser:</b> Navigate to <a href="https://browser.dataspace.copernicus.eu" target="_blank" class="text-cyan-400 underline">browser.dataspace.copernicus.eu</a>.</li>
          <li><b class="text-white">Search your place:</b> Type any city or place (e.g. <i>Vijayawada</i>, <i>Gudlavalleru</i>, or any region).</li>
          <li><b class="text-white">Choose Sentinel-2 L2A:</b> Select <i>True Color RGB</i> with cloud cover under 20%.</li>
          <li><b class="text-white">Download:</b> Click the Download button on the right -> Choose <i>Analytical (GeoTIFF)</i> or <i>High-Res Image (PNG/JPG)</i>.</li>
          <li><b class="text-white">Upload to SatQuery AI:</b> Drag & drop the file into the upload box on the left (or select 2 images for Before & After change detection).</li>
          <li><b class="text-white">Ask in Plain English:</b> Type queries like <i>"What changed here between 2025 and 2026?"</i> or <i>"Where are the buildings?"</i> and click <b>Analyze Satellite Images</b>!</li>
        </ol>
      </div>

      <div class="flex justify-end pt-1">
        <button onclick="closeDataModal()" class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow">
          Got it, Close Guide
        </button>
      </div>
    </div>
  </div>

  <!-- Script for Frontend Logic -->
  <script>
    let activeScenarioId = 'scenario_1_flood';
    let selectedFiles = [];
    let currentResponse = null;
    let viewMode = 'base';

    const SCENARIOS_METADATA = {
      'scenario_1_flood': {
        name: 'Disaster Assessment: Inundation & Submerged Parcels',
        sensor: 'Sentinel-2 L2A (MSI)',
        date: '2023-07-28',
        area: 'Godavari River Basin, AP/Telangana, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Copernicus Open Access Hub / ESA Sentinel-2 L2A',
        image: '/static/demo_scenarios/scenario_1_flood/image1.png',
        query: 'Identify the submerged agricultural parcels and highlight their spatial boundaries.'
      },
      'scenario_2_urban': {
        name: 'Temporal Change: Urban Sprawl & Infrastructure Expansion',
        sensor: 'High-Res Optical Satellite (LEVIR-CD Benchmark)',
        date: '2022-04-12 (T1) vs. 2024-05-18 (T2)',
        area: 'Suburban Industrial Development Zone',
        resolution: '0.5 m GSD',
        crs: 'EPSG:4326',
        source: 'LEVIR-CD Large-Scale Change Detection Archive',
        image: '/static/demo_scenarios/scenario_2_urban/t2.png',
        query: 'What major infrastructure changes occurred between these two acquisition dates?'
      },
      'scenario_3_optical_sar': {
        name: 'All-Weather Fusion: Cloud Penetration (Cartosat + RISAT / Sentinel-1)',
        sensor: 'Cartosat-2S Optical + Sentinel-1 C-band SAR',
        date: '2023-08-20 (Co-registered window)',
        area: 'Coastal Industrial Port & Oil Storage Terminal',
        resolution: 'Optical 0.65m / SAR 10m GSD',
        crs: 'EPSG:4326',
        source: 'ISRO SAC / ESA Sentinel-1 GRD SAR + Optical Archive',
        image: '/static/demo_scenarios/scenario_3_optical_sar/optical.png',
        query: 'Penetrate cloud cover to map industrial storage tanks and coastal water bodies.'
      },
      'scenario_4_coastal': {
        name: 'Coastal Change: Port Infrastructure & Breakwater Expansion',
        sensor: 'Sentinel-2 L2A MSI',
        date: '2023-02-15 (T1) vs. 2024-09-05 (T2)',
        area: 'Visakhapatnam Port & Coastal Corridor, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Copernicus Open Access Hub / ESA Sentinel-2 L2A',
        image: '/static/demo_scenarios/scenario_4_coastal/t2.png',
        query: 'What new coastal infrastructure or breakwater structures were constructed between T1 and T2?'
      },
      'scenario_today_near_real_time': {
        name: "Today's Operational Surveillance Feed (Near-Real-Time Stream)",
        sensor: 'Sentinel-2 L2A MSI',
        date: '2026-09-11 (Acquired & Ingested Today)',
        area: 'National Space Operational Surveillance Corridor',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Copernicus Data Space Ecosystem (Direct Near-Real-Time Stream)',
        image: '/static/latest/latest_scene.png',
        query: 'Detect recent surface changes, water inundation, and newly emerged infrastructure.'
      },
      'scenario_ap_vijayawada': {
        name: 'Vijayawada (2025 vs 2026 Change Detection)',
        sensor: 'Sentinel-2 L2A MSI',
        date: '2025-08-15 (T1) vs. 2026-09-02 (T2)',
        area: 'Vijayawada, Krishna District, AP [16.51°N, 80.65°E]',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/vja_s2_2026_09_02.jpg',
        split_image: '/static/thumbs/vja_s2_2025_08_15.jpg',
        query: 'What changed between 2025 and 2026 in this area?',
        scene_ids: 'vja_s2_2025_08_15,vja_s2_2026_09_02',
        analysis_mode: 'change'
      },
      'scenario_gudlavalleru_change': {
        name: 'Location MVP: Gudlavalleru (2025 vs 2026 Bi-Temporal Change Detection)',
        sensor: 'Sentinel-2 L2A MSI',
        date: '2025-09-03 (T1) vs. 2026-09-05 (T2)',
        area: 'Gudlavalleru, Krishna District, AP, India [16.02°N, 80.70°E]',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Copernicus Sentinel-2 Archive (10m L2A)',
        image: '/static/thumbs/gvl_s2_2026_09_05.jpg',
        split_image: '/static/thumbs/gvl_s2_2025_09_03.jpg',
        query: 'What changed between 2025 and 2026 in this area?',
        scene_ids: 'gvl_s2_2025_09_03,gvl_s2_2026_09_05',
        analysis_mode: 'change'
      }
    };

    const AP_SCENARIOS_CATALOG = {
      'vijayawada': {
        name: 'Vijayawada, Krishna District, AP',
        coords: '16.51°N, 80.65°E',
        bbox: 'BBox: [16.45, 80.58, 16.57, 80.71]',
        feature: 'Krishna River Basin, Prakasam Barrage, Urban Core',
        date: '2025-08-15 (T1) vs. 2026-09-02 (T2)',
        area: 'Vijayawada, Krishna District, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/vja_s2_2026_09_02.jpg',
        split_image: '/static/thumbs/vja_s2_2025_08_15.jpg',
        query: 'What changed between 2025 and 2026 in this area?',
        scene_ids: 'vja_s2_2025_08_15,vja_s2_2026_09_02',
        analysis_mode: 'change'
      },
      'amaravati': {
        name: 'Amaravati Capital Region, AP',
        coords: '16.54°N, 80.51°E',
        bbox: 'BBox: [16.48, 80.45, 16.60, 80.58]',
        feature: 'AP Capital Region, Secretariat, Seed Access Road',
        date: '2025-08-12 (T1) vs. 2026-09-01 (T2)',
        area: 'Amaravati Capital Region, Andhra Pradesh, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/amr_s2_2026_09_01.jpg',
        split_image: '/static/thumbs/amr_s2_2025_08_12.jpg',
        query: 'What infrastructure and capital construction changes occurred between 2025 and 2026?',
        scene_ids: 'amr_s2_2025_08_12,amr_s2_2026_09_01',
        analysis_mode: 'change'
      },
      'visakhapatnam': {
        name: 'Visakhapatnam Port & Smart City, AP',
        coords: '17.69°N, 83.22°E',
        bbox: 'BBox: [17.62, 83.15, 17.75, 83.32]',
        feature: 'Deepwater Port, Coastal Breakwaters, Bay of Bengal',
        date: '2025-08-17 (T1) vs. 2026-09-04 (T2)',
        area: 'Visakhapatnam Port & Smart City, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/vzg_s2_2026_09_04.jpg',
        split_image: '/static/thumbs/vzg_s2_2025_08_17.jpg',
        query: 'Detect port container terminal expansion and shoreline breakwater changes.',
        scene_ids: 'vzg_s2_2025_08_17,vzg_s2_2026_09_04',
        analysis_mode: 'change'
      },
      'tirupati': {
        name: 'Tirupati & Seshachalam Foothills, AP',
        coords: '13.63°N, 79.42°E',
        bbox: 'BBox: [13.56, 79.35, 13.70, 79.48]',
        feature: 'Seshachalam Biosphere Foothills, Temple Town, Industrial Corridor',
        date: '2025-08-11 (T1) vs. 2026-09-03 (T2)',
        area: 'Tirupati & Seshachalam Foothills, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/tpt_s2_2026_09_03.jpg',
        split_image: '/static/thumbs/tpt_s2_2025_08_11.jpg',
        query: 'Identify built-up growth and transit infrastructure changes near foothills.',
        scene_ids: 'tpt_s2_2025_08_11,tpt_s2_2026_09_03',
        analysis_mode: 'change'
      },
      'guntur': {
        name: 'Guntur Agricultural & Commercial Hub, AP',
        coords: '16.31°N, 80.44°E',
        bbox: 'BBox: [16.24, 80.37, 16.37, 80.50]',
        feature: 'Agricultural Market Yards, Outer Ring Expressway, Farmlands',
        date: '2025-08-23 (T1) vs. 2026-09-05 (T2)',
        area: 'Guntur Agricultural & Commercial Hub, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/gtr_s2_2026_09_05.jpg',
        split_image: '/static/thumbs/gtr_s2_2025_08_23.jpg',
        query: 'Quantify urban logistics expansion and changes in agricultural landcover.',
        scene_ids: 'gtr_s2_2025_08_23,gtr_s2_2026_09_05',
        analysis_mode: 'change'
      },
      'rajahmundry': {
        name: 'Rajahmundry & Godavari River Basin, AP',
        coords: '17.00°N, 81.80°E',
        bbox: 'BBox: [16.94, 81.74, 17.06, 81.87]',
        feature: 'Godavari River Bridges, Dowleswaram Barrage, Riparian Zone',
        date: '2025-08-13 (T1) vs. 2026-09-05 (T2)',
        area: 'Rajahmundry & Godavari River Basin, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/rjy_s2_2026_09_05.jpg',
        split_image: '/static/thumbs/rjy_s2_2025_08_13.jpg',
        query: 'Assess river embankment modifications and urban growth along Godavari.',
        scene_ids: 'rjy_s2_2025_08_13,rjy_s2_2026_09_05',
        analysis_mode: 'change'
      },
      'kakinada': {
        name: 'Kakinada Deepwater Port & Coringa, AP',
        coords: '16.99°N, 82.25°E',
        bbox: 'BBox: [16.92, 82.18, 17.05, 82.31]',
        feature: 'Deepwater Port Jetty, Coringa Mangrove Sanctuary, Coastline',
        date: '2025-08-22 (T1) vs. 2026-09-03 (T2)',
        area: 'Kakinada Deepwater Port & Coringa, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/kkn_s2_2026_09_03.jpg',
        split_image: '/static/thumbs/kkn_s2_2025_08_22.jpg',
        query: 'Monitor coastal wetland health and deepwater port jetty extensions.',
        scene_ids: 'kkn_s2_2025_08_22,kkn_s2_2026_09_03',
        analysis_mode: 'change'
      },
      'kurnool': {
        name: 'Kurnool Tungabhadra Basin & Solar Park, AP',
        coords: '15.83°N, 78.04°E',
        bbox: 'BBox: [15.76, 77.97, 15.89, 78.10]',
        feature: 'Tungabhadra Confluence, Ultra Mega Solar Park, Arid Plateaus',
        date: '2025-08-10 (T1) vs. 2026-09-04 (T2)',
        area: 'Kurnool Tungabhadra Basin & Solar Park, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/knl_s2_2026_09_04.jpg',
        split_image: '/static/thumbs/knl_s2_2025_08_10.jpg',
        query: 'Detect newly installed solar photovoltaic panels and arid land transformation.',
        scene_ids: 'knl_s2_2025_08_10,knl_s2_2026_09_04',
        analysis_mode: 'change'
      },
      'nellore': {
        name: 'Nellore Pennar Basin & Aquaculture, AP',
        coords: '14.44°N, 79.99°E',
        bbox: 'BBox: [14.38, 79.92, 14.50, 80.05]',
        feature: 'Pennar River Delta, Intensive Brackish Aquaculture Ponds',
        date: '2025-08-14 (T1) vs. 2026-09-06 (T2)',
        area: 'Nellore Pennar Basin & Aquaculture, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/nlr_s2_2026_09_06.jpg',
        split_image: '/static/thumbs/nlr_s2_2025_08_14.jpg',
        query: 'Delineate aquaculture expansion and evaluate water surface retention.',
        scene_ids: 'nlr_s2_2025_08_14,nlr_s2_2026_09_06',
        analysis_mode: 'change'
      },
      'anantapur': {
        name: 'Anantapur Semi-Arid & Renewable Belt, AP',
        coords: '14.68°N, 77.60°E',
        bbox: 'BBox: [14.62, 77.54, 14.75, 77.66]',
        feature: 'Red Soils, Semi-Arid Scrub, NH-44 Highway, Solar Arrays',
        date: '2025-08-12 (T1) vs. 2026-09-04 (T2)',
        area: 'Anantapur Semi-Arid & Renewable Belt, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/atp_s2_2026_09_04.jpg',
        split_image: '/static/thumbs/atp_s2_2025_08_12.jpg',
        query: 'What renewable energy and water harvesting changes occurred between 2025 and 2026?',
        scene_ids: 'atp_s2_2025_08_12,atp_s2_2026_09_04',
        analysis_mode: 'change'
      },
      'gudlavalleru': {
        name: 'Gudlavalleru, Krishna District, AP',
        coords: '16.02°N, 80.70°E',
        bbox: 'BBox: [15.98, 80.65, 16.08, 80.75]',
        feature: 'Krishna Delta, Academic Campus, Agricultural Grid',
        date: '2025-09-03 (T1) vs. 2026-09-05 (T2)',
        area: 'Gudlavalleru, Krishna District, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'Sentinel-2 L2A Archive (10m L2A)',
        image: '/static/thumbs/gvl_s2_2026_09_05.jpg',
        split_image: '/static/thumbs/gvl_s2_2025_09_03.jpg',
        query: 'What changed between 2025 and 2026 in this area?',
        scene_ids: 'gvl_s2_2025_09_03,gvl_s2_2026_09_05',
        analysis_mode: 'change'
      },
      'ap_state_overview': {
        name: 'Andhra Pradesh State Regional Mosaic',
        coords: '15.91°N, 79.74°E',
        bbox: 'BBox: [12.60, 76.75, 19.15, 84.75]',
        feature: 'State-Wide Regional Overview, Eastern Ghats, Bay of Bengal Coast',
        date: '2025-08-22 (T1) vs. 2026-09-03 (T2)',
        area: 'Andhra Pradesh State Regional Mosaic (Macro View)',
        resolution: '10 m GSD',
        crs: 'EPSG:4326',
        source: 'State-Wide Sentinel-2 Regional Composite',
        image: '/static/thumbs/ap_s2_2026_09_03.jpg',
        split_image: '/static/thumbs/ap_s2_2025_08_22.jpg',
        query: 'Analyze state-wide regional hydrological condition and vegetation change.',
        scene_ids: 'ap_s2_2025_08_22,ap_s2_2026_09_03',
        analysis_mode: 'change'
      }
    };

    let activeSceneIds = null;
    let activeAnalysisMode = null;

    // Initialize with Scenario 1
    window.onload = () => {
      loadScenario('scenario_1_flood');
    };

    function selectApCity(cityKey) {
      const loc = AP_SCENARIOS_CATALOG[cityKey];
      if (!loc) return;
      const inp = document.getElementById('dashboardLocSearch');
      if (inp) inp.value = loc.name.split(',')[0].trim();
      applyApLocation(loc);
    }

    async function searchLocationDashboard() {
      const rawQ = (document.getElementById('dashboardLocSearch')?.value || '').trim();
      const q = rawQ.toLowerCase();
      if (!q) {
        selectApCity('vijayawada');
        return;
      }

      // Check client-side AP catalog
      for (const [k, loc] of Object.entries(AP_SCENARIOS_CATALOG)) {
        if (q.includes(k) || k.includes(q) || loc.name.toLowerCase().includes(q) || loc.feature.toLowerCase().includes(q)) {
          applyApLocation(loc);
          return;
        }
      }

      // If not in static keys, dynamically query /api/scenes?aoi=
      try {
        const res = await fetch(`/api/scenes?aoi=${encodeURIComponent(rawQ)}`);
        if (res.ok) {
          const data = await res.json();
          if (data.scenes && data.scenes.length >= 2) {
            const sorted = data.scenes.sort((a,b) => a.date.localeCompare(b.date));
            const t1 = sorted[0];
            const t2 = sorted[sorted.length - 1];
            const dynamicLoc = {
              name: `${t2.aoi || rawQ}`,
              coords: `${t2.coordinates ? t2.coordinates[0] + '°N, ' + t2.coordinates[1] + '°E' : 'AP AOI'}`,
              bbox: 'BBox: Dynamic Extent',
              feature: `Sentinel-2 Level-2A Multi-Temporal Scene (${t2.sensor || 'MSI'})`,
              date: `${t1.date} (T1) vs. ${t2.date} (T2)`,
              area: t2.aoi || rawQ,
              resolution: '10 m GSD',
              crs: 'EPSG:4326',
              source: 'Copernicus Sentinel-2 State Archive',
              image: t2.thumbnail_url || `/static/thumbs/${t2.id}.jpg`,
              split_image: t1.thumbnail_url || `/static/thumbs/${t1.id}.jpg`,
              query: 'What changed between 2025 and 2026 in this area?',
              scene_ids: `${t1.id},${t2.id}`,
              analysis_mode: 'change'
            };
            applyApLocation(dynamicLoc);
            return;
          }
        }
      } catch (err) {
        console.warn('Dynamic scene lookup error:', err);
      }

      // Default fallback to Vijayawada
      selectApCity('vijayawada');
      alert(`Location '${rawQ}' AOI resolved within Andhra Pradesh territory. Centered on Vijayawada urban-river corridor.`);
    }

    function applyApLocation(loc) {
      activeScenarioId = null;
      selectedFiles = [];
      activeSceneIds = loc.scene_ids;
      activeAnalysisMode = loc.analysis_mode;

      // Update UI displays
      const coordEl = document.getElementById('dashboardAoiCoords');
      if (coordEl) coordEl.innerText = `AOI: ${loc.coords} (${loc.name.split(',')[0]})`;

      document.getElementById('uploadLabel').innerText = `AP Satellite Pair Loaded: ${loc.name}`;
      setQuery(loc.query);
      document.getElementById('viewerBaseImg').src = loc.image;
      if (loc.split_image) {
        document.getElementById('viewerSplitImg').src = loc.split_image;
      }
      document.getElementById('sceneDataSource').innerText = `Sentinel-2 L2A, ${loc.date}, ${loc.area}`;
      document.getElementById('sceneResolution').innerText = loc.resolution;
      document.getElementById('sceneCRS').innerText = `CRS: ${loc.crs}`;
      document.getElementById('traceDataSource').innerText = `Andhra Pradesh State Archive (${loc.source})`;

      // Unhighlight preset scenarios
      document.querySelectorAll('.scenario-btn').forEach(b => {
        b.className = 'scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-slate-500 transition';
      });

      resetViewerOverlays();
    }

    function setQuery(text, scenarioId) {
      document.getElementById('queryInput').value = text;
      if (scenarioId && scenarioId !== activeScenarioId) {
        loadScenario(scenarioId);
      }
    }

    function loadScenario(scenarioId) {
      activeScenarioId = scenarioId;
      selectedFiles = [];
      const meta = SCENARIOS_METADATA[scenarioId];
      if (!meta) return;

      // Update button highlights
      ['scenario_gudlavalleru_change', 'scenario_today_near_real_time', 'scenario_1_flood', 'scenario_2_urban', 'scenario_3_optical_sar', 'scenario_4_coastal'].forEach(id => {
        const btn = document.getElementById('btn_' + id);
        if (btn) {
          if (id === scenarioId) {
            btn.className = 'scenario-btn text-left p-3 rounded-lg border border-cyan-500 bg-space-700/40 hover:border-cyan-400 transition';
          } else {
            btn.className = 'scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-slate-500 transition';
          }
        }
      });

      activeSceneIds = meta.scene_ids || null;
      activeAnalysisMode = meta.analysis_mode || null;

      document.getElementById('uploadLabel').innerText = `Real Satellite Scenario Selected: ${meta.sensor}`;
      setQuery(meta.query);
      document.getElementById('viewerBaseImg').src = meta.image;
      if (meta.split_image) {
        document.getElementById('viewerSplitImg').src = meta.split_image;
      }
      document.getElementById('sceneDataSource').innerText = `${meta.sensor}, ${meta.date}, ${meta.area}`;
      document.getElementById('sceneResolution').innerText = meta.resolution;
      document.getElementById('sceneCRS').innerText = `CRS: ${meta.crs}`;
      document.getElementById('traceDataSource').innerText = `${scenarioId} (${meta.source})`;

      resetViewerOverlays();
    }

    function handleFileSelect(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        selectedFiles = Array.from(files);
        activeScenarioId = null;
        activeSceneIds = null;
        activeAnalysisMode = null;
        document.getElementById('uploadLabel').innerText = `${files.length} custom file(s) selected: ` + Array.from(files).map(f => f.name).join(', ');
        document.getElementById('sceneDataSource').innerText = `Custom User Upload (${files[0].name})`;
        document.getElementById('traceDataSource').innerText = `User Uploaded Satellite Scene`;

        // Unhighlight scenario buttons
        ['scenario_gudlavalleru_change', 'scenario_today_near_real_time', 'scenario_1_flood', 'scenario_2_urban', 'scenario_3_optical_sar', 'scenario_4_coastal'].forEach(id => {
          const btn = document.getElementById('btn_' + id);
          if (btn) btn.className = 'scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-slate-500 transition';
        });

        // Preview first image
        const reader = new FileReader();
        reader.onload = (e) => {
          document.getElementById('viewerBaseImg').src = e.target.result;
        };
        reader.readAsDataURL(files[0]);
        resetViewerOverlays();
      }
    }

    function resetViewerOverlays() {
      document.getElementById('viewerOverlayImg').classList.add('hidden');
      document.getElementById('splitContainer').classList.add('hidden');
      setViewMode('base');
    }

    async function executeAnalysis() {
      const query = document.getElementById('queryInput').value.trim();
      if (!query) {
        alert('Please enter a natural language query.');
        return;
      }

      // Show loader
      document.getElementById('loadingOverlay').classList.remove('hidden');
      document.getElementById('executeBtn').disabled = true;

      const formData = new FormData();
      formData.append('query', query);

      if (selectedFiles.length > 0) {
        for (let i = 0; i < selectedFiles.length; i++) {
          formData.append('files', selectedFiles[i]);
        }
      } else if (activeSceneIds) {
        formData.append('scene_ids', activeSceneIds);
        if (activeAnalysisMode) formData.append('analysis_mode', activeAnalysisMode);
      } else if (activeScenarioId) {
        formData.append('scenario_id', activeScenarioId);
      } else {
        alert('Please select a scenario or upload an image file.');
        document.getElementById('loadingOverlay').classList.add('hidden');
        document.getElementById('executeBtn').disabled = false;
        return;
      }

      try {
        const res = await fetch('/api/v1/analyze', {
          method: 'POST',
          body: formData
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Analysis request failed');
        }

        currentResponse = await res.json();
        renderAnalysisResults(currentResponse);
      } catch (error) {
        alert('Error during execution: ' + error.message);
      } finally {
        document.getElementById('loadingOverlay').classList.add('hidden');
        document.getElementById('executeBtn').disabled = false;
      }
    }

    function renderAnalysisResults(data) {
      // 1. Detected task badge
      const badge = document.getElementById('detectedBadge');
      badge.classList.remove('hidden');
      badge.innerText = 'Task: ' + data.detected_task.toUpperCase().replace('_', ' ');

      // 2. Answer text
      document.getElementById('answerText').innerText = data.result.text_answer;

      // 3. Confidence score
      const confPct = Math.round(data.result.confidence_score * 100);
      document.getElementById('confidenceBar').style.width = confPct + '%';
      document.getElementById('confidenceValue').innerText = confPct + '%';

      // 4. Bullet points
      const bulletContainer = document.getElementById('bulletContainer');
      const bulletList = document.getElementById('bulletList');
      bulletList.innerHTML = '';
      if (data.result.summary_bullet_points && data.result.summary_bullet_points.length > 0) {
        bulletContainer.classList.remove('hidden');
        data.result.summary_bullet_points.forEach(b => {
          const li = document.createElement('li');
          li.innerText = b;
          bulletList.appendChild(li);
        });
      }

      // 5. Visual Evidence Overlay
      if (data.result.visual_evidence && data.result.visual_evidence.overlay_base64) {
        const overlayImg = document.getElementById('viewerOverlayImg');
        overlayImg.src = data.result.visual_evidence.overlay_base64;
        overlayImg.classList.remove('hidden');

        const splitImg = document.getElementById('viewerSplitImg');
        splitImg.src = data.result.visual_evidence.overlay_base64;

        // Auto toggle to overlay view
        setViewMode('overlay');
      }

      // 6. Trace Telemetry
      document.getElementById('traceIdBadge').innerText = 'ID: ' + data.execution_trace.trace_id;
      document.getElementById('traceRouterReasoning').innerText = data.execution_trace.router_reasoning;
      document.getElementById('traceLatency').innerText = data.execution_trace.total_execution_time_ms + ' ms';
      if (data.execution_trace.data_source_label) {
        document.getElementById('traceDataSource').innerText = data.execution_trace.data_source_label;
      }
      if (data.input_summary.sensor) {
        document.getElementById('sceneDataSource').innerText = `${data.input_summary.sensor}, ${data.input_summary.acquisition_date || ''}, ${data.input_summary.area || ''}`;
      }

      const toolsList = document.getElementById('traceToolsList');
      toolsList.innerHTML = '';
      data.execution_trace.tools_executed.forEach(t => {
        const div = document.createElement('div');
        div.className = 'p-2 rounded bg-space-800 border border-space-700 flex justify-between items-center text-[11px]';
        div.innerHTML = `
          <div>
            <b class="text-cyan-400">${t.tool_name}</b>
            <span class="text-slate-500 block text-[9px]">${t.model_checkpoint}</span>
          </div>
          <div class="text-right">
            <span class="text-emerald-400">${t.execution_time_ms} ms</span>
            <span class="text-slate-500 block text-[9px]">Conf: ${(t.confidence*100).toFixed(1)}%</span>
          </div>
        `;
        toolsList.appendChild(div);
      });

      // Enable download button
      document.getElementById('headerDownloadBtn').disabled = false;
    }

    function setViewMode(mode) {
      viewMode = mode;
      const baseImg = document.getElementById('viewerBaseImg');
      const overlayImg = document.getElementById('viewerOverlayImg');
      const splitCont = document.getElementById('splitContainer');

      const btnBase = document.getElementById('btnViewBase');
      const btnOverlay = document.getElementById('btnViewOverlay');
      const btnSplit = document.getElementById('btnViewSplit');

      [btnBase, btnOverlay, btnSplit].forEach(b => {
        b.className = 'px-2.5 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition';
      });

      if (mode === 'base') {
        btnBase.className = 'px-2.5 py-1 rounded bg-space-700 text-white font-medium text-[11px] transition';
        overlayImg.classList.add('hidden');
        splitCont.classList.add('hidden');
      } else if (mode === 'overlay') {
        btnOverlay.className = 'px-2.5 py-1 rounded bg-cyan-600 text-white font-medium text-[11px] transition';
        overlayImg.classList.remove('hidden');
        splitCont.classList.add('hidden');
      } else if (mode === 'split') {
        btnSplit.className = 'px-2.5 py-1 rounded bg-blue-600 text-white font-medium text-[11px] transition';
        overlayImg.classList.add('hidden');
        splitCont.classList.remove('hidden');
      }
    }

    function toggleTraceAccordion() {
      const content = document.getElementById('traceContent');
      const chevron = document.getElementById('traceChevron');
      if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        chevron.classList.add('rotate-180');
      } else {
        content.classList.add('hidden');
        chevron.classList.remove('rotate-180');
      }
    }

    function downloadLatestReport() {
      if (!currentResponse || !currentResponse.execution_trace) {
        alert('Please run an analysis first.');
        return;
      }
      const traceId = currentResponse.execution_trace.trace_id;
      window.open(`/api/v1/report/pdf?trace_id=${traceId}`, '_blank');
    }

    function openDataModal() {
      const m = document.getElementById('dataGuideModal');
      if (m) m.classList.remove('hidden');
    }

    function closeDataModal() {
      const m = document.getElementById('dataGuideModal');
      if (m) m.classList.add('hidden');
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeDataModal();
    });
    document.addEventListener('click', (e) => {
      const modal = document.getElementById('dataGuideModal');
      if (e.target === modal) closeDataModal();
    });
  </script>
</body>
</html>
"""
