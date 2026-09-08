import os
import io
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
from backend.app.utils.image_io import load_image_from_bytes
from backend.app.utils.geo_utils import detect_modality_heuristics
from backend.app.utils.report_generator import generate_mission_pdf_report
from backend.app.agent.controller import controller
from backend.app.agent.registry import registry

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
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# In-memory store for session traces and cached payloads
SESSION_TRACES: Dict[str, Dict[str, Any]] = {}

# Pre-defined SIH 2026 Demonstration Scenarios
DEMO_SCENARIOS = [
    DemoScenario(
        id="scenario_1_flood",
        title="Disaster Assessment: Inundation & Submerged Parcels",
        category="Single-Image VQA & Grounding",
        description="Sentinel-2 optical acquisition over Godavari flood basin. Evaluates inundated area and delineates flood perimeters.",
        default_query="Identify the submerged agricultural parcels and highlight their spatial boundaries.",
        image_paths=["/static/samples/flood_sentinel2_optical.png"],
        input_type="single"
    ),
    DemoScenario(
        id="scenario_2_urban",
        title="Temporal Change: Urban Sprawl & Infrastructure Expansion",
        category="Bi-Temporal Change Analysis (CDVQA)",
        description="Pre-construction 2022 vs Post-construction 2024 Sentinel-2 pair. Quantifies industrial land conversion and highway paving.",
        default_query="What major infrastructure changes occurred between these two acquisition dates?",
        image_paths=["/static/samples/urban_t1_2022.png", "/static/samples/urban_t2_2024.png"],
        input_type="bitemporal_pair"
    ),
    DemoScenario(
        id="scenario_3_optical_sar",
        title="All-Weather Fusion: Cloud Penetration (Cartosat + RISAT)",
        category="Optical-SAR Cross-Modal Fusion",
        description="Cloud-occluded optical image paired with co-registered C-band SAR backscatter. Pierces cloud cover to locate metal tanks & coastline.",
        default_query="Penetrate cloud cover to map industrial storage tanks and coastal water bodies.",
        image_paths=["/static/samples/co_registered_optical_cloudy.png", "/static/samples/co_registered_sar_risat.png"],
        input_type="optical_sar_pair"
    ),
]


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "ps_id": settings.SIH_PS_ID,
        "organization": settings.ORGANIZATION,
        "device": settings.DEVICE,
        "registered_tools": registry.list_tools()
    }


@app.get("/api/v1/scenarios", response_model=List[DemoScenario])
def get_scenarios():
    return DEMO_SCENARIOS


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_remote_sensing_query(
    query: str = Form(...),
    task_hint: Optional[str] = Form("auto"),
    scenario_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Primary agentic remote-sensing query endpoint.
    Accepts either uploaded image files or a pre-loaded scenario ID.
    """
    raw_images = []
    filenames = []
    modalities = []

    # Handle scenario shortcut if provided
    if scenario_id:
        scenario = next((s for s in DEMO_SCENARIOS if s.id == scenario_id), None)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
        
        for rel_path in scenario.image_paths:
            # rel_path looks like /static/samples/xyz.png
            file_name = os.path.basename(rel_path)
            disk_path = settings.SAMPLES_DIR / file_name
            if not disk_path.exists():
                raise HTTPException(status_code=500, detail=f"Sample file missing: {file_name}")
            with open(disk_path, "rb") as f:
                content = f.read()
            arr, _ = load_image_from_bytes(content)
            raw_images.append(arr)
            filenames.append(file_name)
            modalities.append(detect_modality_heuristics(file_name, arr.shape[2] if arr.ndim == 3 else 1, arr))
    else:
        # Validate uploaded files
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="Must upload 1 or 2 satellite images or specify a scenario_id.")
        validated_files = await validate_upload_files(files)
        for content, fname in validated_files:
            arr, _ = load_image_from_bytes(content)
            raw_images.append(arr)
            filenames.append(fname)
            modalities.append(detect_modality_heuristics(fname, arr.shape[2] if arr.ndim == 3 else 1, arr))

    # Execute Agent Controller
    response = controller.execute(
        query=query,
        images=raw_images,
        modalities=modalities,
        image_names=filenames,
        task_hint=task_hint
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

    <!-- Left Controls Panel: Query & Scenarios (5 Cols) -->
    <div class="lg:col-span-5 space-y-5 flex flex-col">

      <!-- SIH Pre-Configured Scenarios -->
      <div class="bg-space-800 border border-space-700 rounded-xl p-4 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <i class="fa-solid fa-bolt text-yellow-400"></i>
            <span>ISRO Demonstration Scenarios</span>
          </h2>
          <span class="text-[10px] text-slate-400">Instant 1-Click Test</span>
        </div>
        
        <div class="grid grid-cols-1 gap-2" id="scenariosContainer">
          <button onclick="loadScenario('scenario_1_flood')" class="scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-cyan-500 hover:bg-space-700/50 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-cyan-300">1. Flood Inundation & Grounding</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300">Single Optical</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Sentinel-2 flood scene. Evaluates submerged parcel acreage & draws masks.</p>
          </button>

          <button onclick="loadScenario('scenario_2_urban')" class="scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-cyan-500 hover:bg-space-700/50 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-amber-300">2. Bi-Temporal Urban Expansion</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-900/60 text-amber-300">T1/T2 Pair (CDVQA)</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">2022 vs 2024 pair. Siamese difference engine maps industrial expansion.</p>
          </button>

          <button onclick="loadScenario('scenario_3_optical_sar')" class="scenario-btn text-left p-3 rounded-lg border border-space-700 bg-space-900/60 hover:border-cyan-500 hover:bg-space-700/50 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-purple-300">3. Optical-SAR Cloud Penetration</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-900/60 text-purple-300">Cartosat + RISAT</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Pierces heavy cloud occlusion to isolate oil tanks and coastline via SAR.</p>
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
          <button onclick="setQuery('Identify the submerged agricultural parcels and highlight their spatial boundaries.')" class="text-[10px] bg-space-900 border border-space-700 hover:border-slate-500 px-2 py-1 rounded text-slate-300">💧 Flood Extent</button>
          <button onclick="setQuery('What major infrastructure changes occurred between these two acquisition dates?')" class="text-[10px] bg-space-900 border border-space-700 hover:border-slate-500 px-2 py-1 rounded text-slate-300">🏗️ Urban Growth</button>
          <button onclick="setQuery('Penetrate cloud cover to map industrial storage tanks and coastal water bodies.')" class="text-[10px] bg-space-900 border border-space-700 hover:border-slate-500 px-2 py-1 rounded text-slate-300">🛰️ Cloud Penetration</button>
          <button onclick="setQuery('Highlight the water reservoir and estimate coverage hectares.')" class="text-[10px] bg-space-900 border border-space-700 hover:border-slate-500 px-2 py-1 rounded text-slate-300">🎯 Bounding Box</button>
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
          <img id="viewerBaseImg" src="/static/samples/flood_sentinel2_optical.png" alt="Base Satellite View" class="absolute inset-0 w-full h-full object-contain">
          
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

        <!-- Viewport Metadata Footer -->
        <div class="mt-2 flex items-center justify-between text-[11px] text-slate-400 px-1">
          <span id="sceneDimensions">Dimensions: 512 x 512 px</span>
          <span id="sceneCRS">CRS: EPSG:4326 &bull; GSD: 10m</span>
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
          Select a demonstration scenario on the left or enter a natural language query and click <b>Execute Agentic Analysis</b>.
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

    // Initialize with Scenario 1
    window.onload = () => {
      loadScenario('scenario_1_flood');
    };

    function setQuery(text) {
      document.getElementById('queryInput').value = text;
    }

    function loadScenario(scenarioId) {
      activeScenarioId = scenarioId;
      selectedFiles = [];
      document.getElementById('uploadLabel').innerText = 'Scenario selected: ' + scenarioId;

      if (scenarioId === 'scenario_1_flood') {
        setQuery('Identify the submerged agricultural parcels and highlight their spatial boundaries.');
        document.getElementById('viewerBaseImg').src = '/static/samples/flood_sentinel2_optical.png';
      } else if (scenarioId === 'scenario_2_urban') {
        setQuery('What major infrastructure changes occurred between these two acquisition dates?');
        document.getElementById('viewerBaseImg').src = '/static/samples/urban_t2_2024.png';
      } else if (scenarioId === 'scenario_3_optical_sar') {
        setQuery('Penetrate cloud cover to map industrial storage tanks and coastal water bodies.');
        document.getElementById('viewerBaseImg').src = '/static/samples/co_registered_optical_cloudy.png';
      }
      resetViewerOverlays();
    }

    function handleFileSelect(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        selectedFiles = Array.from(files);
        activeScenarioId = null;
        document.getElementById('uploadLabel').innerText = `${files.length} custom file(s) selected: ` + Array.from(files).map(f => f.name).join(', ');
        
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
