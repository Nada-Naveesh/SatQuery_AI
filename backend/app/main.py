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
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Primary agentic remote-sensing query endpoint.
    Accepts either user-uploaded satellite image files (GeoTIFF/PNG/JPEG)
    or a pre-configured real satellite scenario ID.
    """
    raw_images = []
    filenames = []
    modalities = []
    scenario_meta = {}

    # 1. Handle preloaded real satellite scenario
    if scenario_id:
        if scenario_id == "scenario_today_near_real_time":
            scenario = catalog_service.get_todays_scenario()
            scenario_meta = scenario.model_dump()
            latest_tif = settings.DATA_DIR / "latest" / "latest_scene.tif"
            latest_png = settings.DATA_DIR / "latest" / "latest_scene.png"
            target_fpath = latest_tif if latest_tif.exists() else (latest_png if latest_png.exists() else None)
            if target_fpath:
                arr, _ = load_image_from_path(target_fpath)
                raw_images.append(arr)
                filenames.append(target_fpath.name)
                modalities.append(detect_modality_heuristics(target_fpath.name, arr.shape[2] if arr.ndim == 3 else 1, arr))
            else:
                # Fallback to scenario 1
                fallback_path = settings.DEMO_SCENARIOS_DIR / "scenario_1_flood" / "image1.tif"
                arr, _ = load_image_from_path(fallback_path)
                raw_images.append(arr)
                filenames.append(fallback_path.name)
                modalities.append("optical_multispectral")
        else:
            scenarios = get_all_scenarios()
            scenario = next((s for s in scenarios if s.id == scenario_id), None)
            if not scenario:
                raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
            
            scenario_meta = scenario.model_dump()
            s_dir = settings.DEMO_SCENARIOS_DIR / scenario_id

        if s_dir.exists():
            # Check for authentic GeoTIFF .tif files first, or fallback to .png
            tif_files = sorted(s_dir.glob("*.tif"))
            png_files = sorted(s_dir.glob("*.png"))
            load_targets = tif_files if tif_files else png_files
            for fpath in load_targets:
                arr, _ = load_image_from_path(fpath)
                raw_images.append(arr)
                filenames.append(fpath.name)
                modalities.append(detect_modality_heuristics(fpath.name, arr.shape[2] if arr.ndim == 3 else 1, arr))
        else:
            # Fallback to static samples if demo_scenarios folder missing
            for rel_path in scenario.image_paths:
                fname = os.path.basename(rel_path)
                disk_path = settings.SAMPLES_DIR / fname
                if not disk_path.exists():
                    raise HTTPException(status_code=500, detail=f"Sample file missing: {fname}")
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
                detail="Must upload 1 or 2 satellite images (GeoTIFF / PNG) or select a pre-configured scenario."
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
    SESSION_TRACES[trace_id] = {
        "query": query,
        "detected_task": response.detected_task,
        "analysis_result": response.result.model_dump(),
        "execution_trace": response.execution_trace.model_dump(),
        "input_summary": response.input_summary.model_dump(),
        "base_image": raw_images[0],
        "evidence_overlay_b64": response.result.visual_evidence.overlay_base64 if response.result.visual_evidence else None
    }

    return response


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
        
        <div class="grid grid-cols-1 gap-2" id="scenariosContainer">
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

        <!-- Suggestion Pills -->
        <div class="flex flex-wrap gap-1.5">
          <button onclick="setQuery('Identify the submerged agricultural parcels and highlight their spatial boundaries.', 'scenario_1_flood')" class="text-[10px] bg-space-900 border border-space-700 hover:border-cyan-500 px-2.5 py-1 rounded text-slate-300 transition">💧 Flood Extent</button>
          <button onclick="setQuery('What major infrastructure changes occurred between these two acquisition dates?', 'scenario_2_urban')" class="text-[10px] bg-space-900 border border-space-700 hover:border-amber-500 px-2.5 py-1 rounded text-slate-300 transition">🏗️ Urban Growth</button>
          <button onclick="setQuery('Penetrate cloud cover to map industrial storage tanks and coastal water bodies.', 'scenario_3_optical_sar')" class="text-[10px] bg-space-900 border border-space-700 hover:border-purple-500 px-2.5 py-1 rounded text-slate-300 transition">🛰️ Cloud Penetration</button>
          <button onclick="setQuery('Highlight the water reservoir and estimate coverage hectares.', 'scenario_1_flood')" class="text-[10px] bg-space-900 border border-space-700 hover:border-slate-500 px-2.5 py-1 rounded text-slate-300 transition">🎯 Bounding Box</button>
        </div>

        <!-- Custom Upload Zone -->
        <div class="border-t border-space-700 pt-3">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Upload Satellite Images (Optional if Scenario Selected)
          </label>
          <div class="border-2 border-dashed border-space-600 hover:border-cyan-500 rounded-lg p-3 text-center cursor-pointer transition bg-space-900/40" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" multiple accept=".tif,.tiff,.png,.jpg,.jpeg" class="hidden" onchange="handleFileSelect(event)">
            <i class="fa-solid fa-cloud-arrow-up text-slate-400 text-lg mb-1"></i>
            <p class="text-xs text-slate-300 font-medium" id="uploadLabel">Upload 1 or 2 files (GeoTIFF / PNG)</p>
            <p class="text-[10px] text-slate-500">Supports Single, Temporal Pairs, or Optical+SAR Pairs</p>
          </div>
        </div>

        <!-- Execute Action Button -->
        <button onclick="executeAnalysis()" id="executeBtn" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-cyan-600/30">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
          <span>Execute Agentic Analysis</span>
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
            <span class="text-xs text-slate-300 font-medium animate-pulse" id="loadingStatusText">Agent Orchestrator Sequencing Specialist Models...</span>
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
            <span id="sceneCRS">CRS: EPSG:4326</span>
          </div>
        </div>
      </div>

      <!-- Grounded Result Card -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <i class="fa-solid fa-clipboard-check text-emerald-400"></i>
            <span>Grounded Operational Answer</span>
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
          Select a real satellite demonstration scenario on the left or enter a query and click <b>Execute Agentic Analysis</b>.
        </div>

        <!-- Key Observations Bullets -->
        <div id="bulletContainer" class="hidden space-y-1.5 pt-1">
          <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Telemetry & Spatial Observations</span>
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
      }
    };

    // Initialize with Scenario 1
    window.onload = () => {
      loadScenario('scenario_1_flood');
    };

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
      ['scenario_today_near_real_time', 'scenario_1_flood', 'scenario_2_urban', 'scenario_3_optical_sar', 'scenario_4_coastal'].forEach(id => {
        const btn = document.getElementById('btn_' + id);
        if (btn) {
          if (id === scenarioId) {
            btn.className = 'scenario-btn text-left p-3 rounded-lg border border-cyan-500 bg-space-700/40 hover:border-cyan-400 transition';
          } else {
            btn.className = 'scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-slate-500 transition';
          }
        }
      });

      document.getElementById('uploadLabel').innerText = `Real Satellite Scenario Selected: ${meta.sensor}`;
      setQuery(meta.query);
      document.getElementById('viewerBaseImg').src = meta.image;
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
        document.getElementById('uploadLabel').innerText = `${files.length} custom file(s) selected: ` + Array.from(files).map(f => f.name).join(', ');
        document.getElementById('sceneDataSource').innerText = `Custom User Upload (${files[0].name})`;
        document.getElementById('traceDataSource').innerText = `User Uploaded Satellite Scene`;

        // Unhighlight scenario buttons
        ['scenario_1_flood', 'scenario_2_urban', 'scenario_3_optical_sar'].forEach(id => {
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
  </script>
</body>
</html>
"""
