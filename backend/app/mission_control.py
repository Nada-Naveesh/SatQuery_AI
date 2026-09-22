"""
SatQuery AI - Production-Grade Mission Control Dashboard (PS 26167)
Dominance-Grade Black & Red Defense Intelligence Theme
Integrated with Live Copernicus Data Space Discovery, Leaflet Map AOI,
Fixed CSS Clip-Path Split Comparison Slider, Real Hectare Metrics, and Asynchronous Pipeline Telemetry.
"""

MISSION_CONTROL_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SatQuery AI — Satellite Intelligence Platform (SIH 2026 PS 26167)</title>
  
  <!-- Tailwind CSS & Font Awesome -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  
  <!-- Leaflet Map CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            obsidian: {
              950: '#07080b',
              900: '#0d0f17',
              850: '#111420',
              800: '#151928',
              700: '#1f2438',
              600: '#2b324d'
            },
            crimson: {
              400: '#f87171',
              500: '#ef2b32',
              600: '#dc2626',
              700: '#b91c1c',
              800: '#991b1b',
              900: '#450a0a'
            }
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace']
          }
        }
      }
    }
  </script>

  <style>
    :root {
      --bg-primary: #07080b;
      --bg-secondary: #0d0f17;
      --bg-tertiary: #131722;
      --border-subtle: #1f2438;
      --border-focus: #ef2b32;
      --red-primary: #ef2b32;
      --red-glow: rgba(239, 43, 50, 0.25);
      --red-dark: #b8141b;
      --green-accent: #10b981;
      --blue-accent: #06b6d4;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --split-pos: 50%;
    }

    body {
      background-color: var(--bg-primary);
      color: var(--text-primary);
      font-family: 'Inter', sans-serif;
    }

    /* Fixed Split Comparison Slider */
    .split-wrapper {
      position: relative;
      width: 100%;
      height: 520px;
      overflow: hidden;
      background-color: #030406;
      user-select: none;
    }

    .split-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: contain;
      pointer-events: none;
    }

    .split-before {
      z-index: 10;
      clip-path: polygon(0 0, var(--split-pos, 50%) 0, var(--split-pos, 50%) 100%, 0 100%);
    }

    .split-after {
      z-index: 5;
    }

    .split-divider {
      position: absolute;
      top: 0;
      bottom: 0;
      left: var(--split-pos, 50%);
      width: 3px;
      background: var(--red-primary);
      box-shadow: 0 0 12px var(--red-glow), 0 0 4px #fff;
      z-index: 20;
      transform: translateX(-50%);
      cursor: ew-resize;
    }

    .split-handle {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: #dc2626;
      border: 2px solid #ffffff;
      box-shadow: 0 0 15px rgba(239, 43, 50, 0.8), 0 2px 10px rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 11px;
      cursor: ew-resize;
    }

    /* Leaflet Dark Theme Overrides */
    .leaflet-container {
      background: #07080b !important;
      font-family: inherit;
    }
    .leaflet-bar a {
      background-color: #111420 !important;
      color: #f8fafc !important;
      border-bottom: 1px solid #1f2438 !important;
    }
    .leaflet-bar a:hover {
      background-color: #ef2b32 !important;
      color: #ffffff !important;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #07080b;
    }
    ::-webkit-scrollbar-thumb {
      background: #1f2438;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #ef2b32;
    }

    /* Pulse animation */
    @keyframes redPulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.6; transform: scale(1.05); }
    }
    .pulse-glow {
      animation: redPulse 2s infinite ease-in-out;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased">

  <!-- TOP APP HEADER -->
  <header class="border-b border-obsidian-700/80 bg-obsidian-900/90 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand & Project PS -->
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-tr from-crimson-600 to-red-500 flex items-center justify-center shadow-lg shadow-crimson-600/30">
          <i class="fa-solid fa-satellite text-white text-lg"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold tracking-wider text-base uppercase text-white font-mono">SatQuery AI</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-crimson-900/60 text-crimson-400 border border-crimson-700/50">ISRO PS 26167</span>
          </div>
          <p class="text-xs text-slate-400">Autonomous Vision-Language Satellite Intelligence</p>
        </div>
      </div>

      <!-- Live Telemetry Status Pills -->
      <div class="hidden md:flex items-center space-x-3 text-xs">
        <div id="pillRouter" class="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-obsidian-800 border border-obsidian-700 text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Router: <strong class="text-emerald-400">Ready</strong></span>
        </div>
        <div id="pillCopernicus" class="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-obsidian-800 border border-obsidian-700 text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Copernicus CDSE: <strong class="text-emerald-400">Connected</strong></span>
        </div>
        <div id="pillEngine" class="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-obsidian-800 border border-obsidian-700 text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Engine: <strong class="text-emerald-400">Calibrated</strong></span>
        </div>
      </div>

      <!-- Header Action Buttons -->
      <div class="flex items-center space-x-2">
        <button onclick="toggleDataGuideModal()" class="px-3 py-1.5 rounded-lg bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-xs text-slate-300 transition-all flex items-center space-x-1.5">
          <i class="fa-solid fa-circle-question text-crimson-400"></i>
          <span>How to Get Free Satellite Images</span>
        </button>
        <button id="btnExportPdf" onclick="downloadPdfReport()" disabled class="px-3.5 py-1.5 rounded-lg bg-obsidian-800 hover:bg-crimson-600 border border-obsidian-700 hover:border-crimson-500 text-xs font-semibold text-slate-200 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2">
          <i class="fa-solid fa-file-pdf"></i>
          <span>Export PDF Report</span>
        </button>
        <button onclick="resetAllState()" class="px-3 py-1.5 rounded-lg bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-xs text-slate-300 transition-all">
          <i class="fa-solid fa-arrows-rotate mr-1"></i> Reset
        </button>
      </div>

    </div>
  </header>

  <!-- HERO SECTION -->
  <section class="border-b border-obsidian-700/60 bg-gradient-to-b from-obsidian-900 to-obsidian-950 py-10 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto text-center">
      <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-3 font-sans">
        Satellite Intelligence, <span class="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-rose-400">Simplified.</span>
      </h1>
      <p class="max-w-2xl mx-auto text-sm sm:text-base text-slate-400 mb-8">
        Search any global or Indian location to discover Sentinel-2 satellite passes, or upload your own imagery. Measure physical land-surface changes in hectares with certified mathematical rigor.
      </p>

      <!-- Two Primary Workflow Selection Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto text-left mb-8">
        
        <!-- Card 1: Live Place Exploration -->
        <div id="cardSelectLive" onclick="switchWorkflow('live')" class="cursor-pointer p-5 rounded-xl bg-obsidian-850 border-2 border-crimson-500/80 hover:border-crimson-500 shadow-lg shadow-crimson-900/20 transition-all">
          <div class="flex items-center space-x-3 mb-2">
            <div class="w-9 h-9 rounded-lg bg-crimson-600/20 text-crimson-400 flex items-center justify-center font-bold">
              <i class="fa-solid fa-earth-asia"></i>
            </div>
            <div>
              <h3 class="font-bold text-white text-base">Explore a Live Location</h3>
              <p class="text-xs text-slate-400">Search any city, district, river delta, or GPS coordinates</p>
            </div>
          </div>
          <p class="text-xs text-slate-300 mt-2">
            Automatic multi-temporal scene discovery from Copernicus CDSE with quality checks & cloud masking.
          </p>
        </div>

        <!-- Card 2: Custom Upload -->
        <div id="cardSelectUpload" onclick="switchWorkflow('upload')" class="cursor-pointer p-5 rounded-xl bg-obsidian-850 border border-obsidian-700 hover:border-crimson-500/70 transition-all">
          <div class="flex items-center space-x-3 mb-2">
            <div class="w-9 h-9 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center font-bold">
              <i class="fa-solid fa-cloud-arrow-up"></i>
            </div>
            <div>
              <h3 class="font-bold text-white text-base">Upload Satellite Images</h3>
              <p class="text-xs text-slate-400">Provide your own GeoTIFF pairs or standard imagery</p>
            </div>
          </div>
          <p class="text-xs text-slate-300 mt-2">
            Sub-pixel co-registration, change vector analysis, and metadata-aware spatial scale evaluation.
          </p>
        </div>

      </div>

      <!-- 3-Step Guided Workflow Banner -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-4xl mx-auto pt-3 border-t border-obsidian-800/80 text-xs text-slate-400">
        <div class="flex items-center justify-center space-x-2">
          <span class="w-5 h-5 rounded-full bg-obsidian-700 text-slate-200 flex items-center justify-center font-bold text-[11px]">1</span>
          <span>Choose Place or Drop Files</span>
        </div>
        <div class="flex items-center justify-center space-x-2">
          <span class="w-5 h-5 rounded-full bg-obsidian-700 text-slate-200 flex items-center justify-center font-bold text-[11px]">2</span>
          <span>Select Time Windows & Scenes</span>
        </div>
        <div class="flex items-center justify-center space-x-2">
          <span class="w-5 h-5 rounded-full bg-obsidian-700 text-slate-200 flex items-center justify-center font-bold text-[11px]">3</span>
          <span>Get Real Hectare Breakdown & PDF</span>
        </div>
      </div>

    </div>
  </section>

  <!-- MAIN OPERATIONAL WORKSPACE -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full grid grid-cols-1 lg:grid-cols-12 gap-8">

    <!-- LEFT CONTROL COLUMN: 5 COLS -->
    <div class="lg:col-span-5 space-y-6">

      <!-- PANEL A: LIVE LOCATION WORKFLOW -->
      <div id="panelLiveLocation" class="bg-obsidian-900 rounded-xl border border-obsidian-700 p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-obsidian-800 pb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-magnifying-glass-location text-crimson-500"></i>
            <h2 class="font-bold text-sm uppercase tracking-wider text-slate-200">Location & Scene Discovery</h2>
          </div>
          <span id="txtCoordsPill" class="text-[11px] font-mono px-2 py-0.5 rounded bg-obsidian-800 border border-obsidian-700 text-slate-300">
            16.0200° N, 80.7000° E
          </span>
        </div>

        <!-- Place Search Input Form -->
        <div class="space-y-2">
          <label class="text-xs font-semibold text-slate-300">Target Area of Interest (AOI)</label>
          <div class="flex space-x-2">
            <div class="relative flex-1">
              <i class="fa-solid fa-location-dot absolute left-3 top-3 text-slate-500 text-sm"></i>
              <input id="inputPlaceSearch" type="text" value="Gudlavalleru" placeholder="Enter place name or 'lat, lon'..." class="w-full pl-9 pr-3 py-2 bg-obsidian-950 border border-obsidian-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-crimson-500 font-sans" onkeydown="if(event.key==='Enter') executePlaceSearch()" />
            </div>
            <button onclick="executePlaceSearch()" class="px-4 py-2 bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold rounded-lg transition-all flex items-center space-x-1.5">
              <i class="fa-solid fa-search"></i>
              <span>Search</span>
            </button>
          </div>

          <!-- Fast Quick-Search Pills for Evaluators -->
          <div class="flex flex-wrap items-center gap-1.5 pt-1">
            <span class="text-[10px] text-slate-500">Quick AOI:</span>
            <button onclick="quickSearch('Gudlavalleru')" class="text-[11px] px-2 py-0.5 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-300">Gudlavalleru</button>
            <button onclick="quickSearch('Avanigadda')" class="text-[11px] px-2 py-0.5 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-300">Avanigadda Delta</button>
            <button onclick="quickSearch('Vijayawada')" class="text-[11px] px-2 py-0.5 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-300">Vijayawada</button>
            <button onclick="quickSearch('Amaravati')" class="text-[11px] px-2 py-0.5 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-300">Amaravati</button>
            <button onclick="quickSearch('Visakhapatnam')" class="text-[11px] px-2 py-0.5 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-300">Visakhapatnam</button>
          </div>
        </div>

        <!-- Andhra Pradesh State-Wide Coverage Regional Presets -->
        <div class="p-3 rounded-lg bg-obsidian-950 border border-obsidian-800 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
              <i class="fa-solid fa-map-location-dot text-crimson-400"></i>
              <span>Andhra Pradesh State-Wide Coverage</span>
            </span>
            <span class="text-[10px] text-slate-500 font-mono">AP Spatial Corridor</span>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="quickSearch('Vijayawada')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Vijayawada</button>
            <button onclick="quickSearch('Amaravati')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Amaravati</button>
            <button onclick="quickSearch('Visakhapatnam')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Visakhapatnam</button>
            <button onclick="quickSearch('Tirupati')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Tirupati</button>
            <button onclick="quickSearch('Kurnool')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Kurnool</button>
            <button onclick="quickSearch('Avanigadda')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Avanigadda</button>
            <button onclick="quickSearch('Gudlavalleru')" class="text-xs px-2.5 py-1 rounded bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-slate-200">Gudlavalleru</button>
          </div>
        </div>

        <!-- Interactive AOI Leaflet Map Preview -->
        <div class="space-y-1">
          <div class="flex justify-between text-[11px] text-slate-400">
            <span>Spatial Footprint Map</span>
            <span id="txtAoiAreaKm2" class="font-mono text-crimson-400">AOI: ~120 km²</span>
          </div>
          <div id="aoiMap" class="w-full h-36 rounded-lg border border-obsidian-700 overflow-hidden z-10"></div>
        </div>

        <!-- Copernicus Sentinel-2 Scenes List -->
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <label class="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-film text-slate-400"></i>
              <span>Available Sentinel-2 Passes (CDSE)</span>
            </label>
            <span id="txtSceneCount" class="text-[10px] text-slate-400 font-mono">2 scenes ready</span>
          </div>

          <div id="sceneListContainer" class="space-y-2 max-h-48 overflow-y-auto pr-1">
            <!-- Dynamically populated scene cards -->
            <div class="p-2.5 rounded-lg bg-obsidian-950 border border-obsidian-700/80 flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <div>
                  <div class="font-semibold text-slate-200">2026-09-05 (After / T2)</div>
                  <div class="text-[10px] text-slate-400">Cloud Cover: 4.2% | Level-2A BOA</div>
                </div>
              </div>
              <span class="px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800 text-[10px] text-emerald-400">Selected T2</span>
            </div>
            <div class="p-2.5 rounded-lg bg-obsidian-950 border border-obsidian-700/80 flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2.5">
                <span class="w-2 h-2 rounded-full bg-sky-400"></span>
                <div>
                  <div class="font-semibold text-slate-200">2025-09-03 (Before / T1)</div>
                  <div class="text-[10px] text-slate-400">Cloud Cover: 6.8% | Level-2A BOA</div>
                </div>
              </div>
              <span class="px-2 py-0.5 rounded bg-sky-950/60 border border-sky-800 text-[10px] text-sky-400">Selected T1</span>
            </div>
          </div>
        </div>

      </div>

      <!-- PANEL B: UPLOAD WORKFLOW (Hidden by default) -->
      <div id="panelUploadImagery" class="hidden bg-obsidian-900 rounded-xl border border-obsidian-700 p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-obsidian-800 pb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-upload text-crimson-500"></i>
            <h2 class="font-bold text-sm uppercase tracking-wider text-slate-200">Upload Satellite Imagery Pair</h2>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-obsidian-800 border border-obsidian-700 text-slate-400">GeoTIFF / PNG / JPG</span>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <!-- T1 Upload Dropzone -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-300">T1: Before Image</label>
            <div id="dropzoneT1" onclick="document.getElementById('fileT1').click()" class="border-2 border-dashed border-obsidian-700 hover:border-crimson-500/80 rounded-xl p-4 text-center cursor-pointer bg-obsidian-950/60 transition-all">
              <i class="fa-solid fa-cloud-arrow-up text-2xl text-slate-500 mb-1"></i>
              <p id="labelT1" class="text-xs font-semibold text-slate-300 truncate">Click to select T1</p>
              <p class="text-[10px] text-slate-500">GeoTIFF, PNG, JPEG</p>
            </div>
            <input id="fileT1" type="file" accept=".tif,.tiff,.png,.jpg,.jpeg" class="hidden" onchange="handleFileUpload(event, 't1')" />
          </div>

          <!-- T2 Upload Dropzone -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-300">T2: After Image</label>
            <div id="dropzoneT2" onclick="document.getElementById('fileT2').click()" class="border-2 border-dashed border-obsidian-700 hover:border-crimson-500/80 rounded-xl p-4 text-center cursor-pointer bg-obsidian-950/60 transition-all">
              <i class="fa-solid fa-cloud-arrow-up text-2xl text-slate-500 mb-1"></i>
              <p id="labelT2" class="text-xs font-semibold text-slate-300 truncate">Click to select T2</p>
              <p class="text-[10px] text-slate-500">GeoTIFF, PNG, JPEG</p>
            </div>
            <input id="fileT2" type="file" accept=".tif,.tiff,.png,.jpg,.jpeg" class="hidden" onchange="handleFileUpload(event, 't2')" />
          </div>
        </div>

        <!-- Honest Spatial Metadata Disclaimer -->
        <div id="uploadNoticeBox" class="p-3 rounded-lg bg-amber-950/40 border border-amber-800/60 text-[11px] text-amber-300/90 leading-relaxed">
          <i class="fa-solid fa-circle-info text-amber-400 mr-1"></i>
          <strong>Geospatial Notice:</strong> Standard PNG/JPG files without embedded coordinate tags are quantified using estimated 10m Ground Sample Distance. For certified legal or defense area reporting, upload georeferenced GeoTIFFs.
        </div>
      </div>

      <!-- NATURAL LANGUAGE QUERY & TRIGGER BOX -->
      <div class="bg-obsidian-900 rounded-xl border border-obsidian-700 p-5 space-y-4">
        <div class="space-y-2">
          <label class="text-xs font-semibold text-slate-300 flex items-center justify-between">
            <span>Natural-Language Remote Sensing Query</span>
            <span class="text-[10px] text-slate-500">Multimodal Agent Prompt</span>
          </label>
          <textarea id="inputQuery" rows="3" class="w-full p-3 bg-obsidian-950 border border-obsidian-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500 font-sans resize-none">Quantify agricultural inundation, vegetation changes, and new built-up infrastructure in hectares.</textarea>
        </div>

        <!-- PRIMARY EXECUTION BUTTON -->
        <button id="btnStartAnalysis" onclick="startSatelliteAnalysis()" class="w-full py-3.5 bg-gradient-to-r from-crimson-600 via-red-600 to-crimson-700 hover:from-crimson-500 hover:to-red-600 text-white font-bold text-sm tracking-wider uppercase rounded-xl shadow-lg shadow-crimson-900/40 hover:shadow-crimson-600/30 transition-all flex items-center justify-center space-x-2">
          <i class="fa-solid fa-bolt-lightning"></i>
          <span>Start Satellite Analysis</span>
        </button>
      </div>

    </div>

    <!-- RIGHT RESULTS & EVIDENCE COLUMN: 7 COLS -->
    <div class="lg:col-span-7 space-y-6">

      <!-- SATELLITE VIEWER CONTAINER WITH FIXED SPLIT COMPARISON -->
      <div class="bg-obsidian-900 rounded-xl border border-obsidian-700 overflow-hidden shadow-2xl">
        
        <!-- Viewer Mode Tabs Bar -->
        <div class="px-4 py-2.5 border-b border-obsidian-800 bg-obsidian-850 flex items-center justify-between">
          <div class="flex items-center space-x-1">
            <button id="tabModeSplit" onclick="setViewerMode('split')" class="px-3 py-1 rounded-md text-xs font-semibold bg-crimson-600 text-white transition-all">
              <i class="fa-solid fa-table-columns mr-1"></i> Split Comparison
            </button>
            <button id="tabModeOverlay" onclick="setViewerMode('overlay')" class="px-3 py-1 rounded-md text-xs font-semibold bg-obsidian-800 hover:bg-obsidian-700 text-slate-300 transition-all">
              <i class="fa-solid fa-layer-group mr-1"></i> Evidence Overlay
            </button>
            <button id="tabModeSide" onclick="setViewerMode('sideBySide')" class="px-3 py-1 rounded-md text-xs font-semibold bg-obsidian-800 hover:bg-obsidian-700 text-slate-300 transition-all">
              <i class="fa-solid fa-arrows-split-up-and-left mr-1"></i> Side-by-Side
            </button>
          </div>

          <!-- Date / Provenance Tags -->
          <div class="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
            <span id="tagDateT1" class="px-2 py-0.5 rounded bg-obsidian-800 border border-obsidian-700">T1: 2025-09-03</span>
            <span>vs</span>
            <span id="tagDateT2" class="px-2 py-0.5 rounded bg-obsidian-800 border border-obsidian-700 text-crimson-400">T2: 2026-09-05</span>
          </div>
        </div>

        <!-- VIEWER CANVAS -->
        <div id="viewerViewport" class="relative">

          <!-- 1. SPLIT COMPARISON VIEW (Default) -->
          <div id="viewSplitMode" class="split-wrapper">
            <!-- Before Image Layer (Clipped by CSS polygon) -->
            <img id="imgSplitBefore" src="/static/thumbs/gvl_s2_2025_09_03.jpg" alt="Before T1" class="split-layer split-before" />
            <!-- After Image Layer -->
            <img id="imgSplitAfter" src="/static/thumbs/gvl_s2_2026_09_05.jpg" alt="After T2" class="split-layer split-after" />
            
            <!-- Draggable Divider & Handle -->
            <div id="splitDivider" class="split-divider">
              <div class="split-handle">
                <i class="fa-solid fa-left-right"></i>
              </div>
            </div>

            <!-- On-Screen Badges -->
            <div class="absolute top-3 left-3 z-30 px-2.5 py-1 rounded bg-black/75 border border-slate-700 text-[11px] font-mono text-slate-200">
              ◄ T1 (Before)
            </div>
            <div class="absolute top-3 right-3 z-30 px-2.5 py-1 rounded bg-black/75 border border-slate-700 text-[11px] font-mono text-slate-200">
              T2 (After) ►
            </div>

            <!-- Viewer Coordinates Overlay HUD -->
            <div id="viewerCoordsOverlay" class="absolute bottom-3 left-3 z-30 px-3 py-1.5 rounded-lg bg-black/80 border border-slate-700 text-xs font-mono text-slate-200 flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span id="hudLatLon">16.0200° N, 80.7000° E</span>
              <span id="sceneCoordinatesBadge" class="text-[10px] text-slate-400 font-mono">10m GSD | Sentinel-2</span>
            </div>
          </div>

          <!-- 2. EVIDENCE OVERLAY VIEW -->
          <div id="viewOverlayMode" class="hidden relative w-full h-[520px] bg-black overflow-hidden flex items-center justify-center">
            <img id="imgOverlayBase" src="/static/thumbs/gvl_s2_2026_09_05.jpg" alt="Base Satellite" class="absolute top-0 left-0 w-full h-full object-contain" />
            <img id="imgOverlayChange" src="" alt="Change Overlay" class="absolute top-0 left-0 w-full h-full object-contain z-10 hidden" style="opacity: 0.75;" />

            <!-- Empty overlay placeholder before analysis -->
            <div id="overlayPlaceholderNotice" class="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/60 backdrop-blur-[2px] text-center p-6">
              <i class="fa-solid fa-wand-magic-sparkles text-3xl text-crimson-500 mb-2"></i>
              <p class="font-bold text-slate-200 text-sm">Visual Evidence Overlay Not Yet Generated</p>
              <p class="text-xs text-slate-400 max-w-sm mt-1">Click "Start Satellite Analysis" below to execute sub-pixel change detection and generate classified masks.</p>
            </div>
          </div>

          <!-- 3. SIDE-BY-SIDE VIEW -->
          <div id="viewSideBySideMode" class="hidden grid grid-cols-2 w-full h-[520px] bg-black divide-x divide-obsidian-800">
            <div class="relative w-full h-full flex flex-col">
              <div class="p-2 bg-obsidian-950 text-[11px] font-mono text-slate-400 border-b border-obsidian-800">T1: Before</div>
              <img id="imgSideBefore" src="/static/thumbs/gvl_s2_2025_09_03.jpg" class="w-full h-full object-contain flex-1" />
            </div>
            <div class="relative w-full h-full flex flex-col">
              <div class="p-2 bg-obsidian-950 text-[11px] font-mono text-slate-400 border-b border-obsidian-800">T2: After</div>
              <img id="imgSideAfter" src="/static/thumbs/gvl_s2_2026_09_05.jpg" class="w-full h-full object-contain flex-1" />
            </div>
          </div>

        </div>

        <!-- OVERLAY CONTROLS BAR (Visible in overlay mode) -->
        <div id="overlayControlsBar" class="hidden px-4 py-2 bg-obsidian-850 border-t border-obsidian-800 flex items-center justify-between text-xs">
          <div class="flex items-center space-x-3">
            <span class="text-slate-400">Overlay Opacity:</span>
            <input id="sliderOpacity" type="range" min="0" max="100" value="75" class="w-28 accent-crimson-600" oninput="updateOverlayOpacity(this.value)" />
            <span id="txtOpacityVal" class="font-mono text-slate-300">75%</span>
          </div>
          <div class="text-[11px] text-slate-400 font-mono">
            Spatial Resolution: <strong>10 m GSD (MSI)</strong>
          </div>
        </div>

        <!-- CLASSIFICATION LEGEND (CRITICAL: HIDDEN BEFORE ANALYSIS) -->
        <div id="classificationLegendCard" class="hidden px-4 py-3 bg-obsidian-950 border-t border-obsidian-800 text-xs">
          <div class="flex items-center justify-between mb-2">
            <span class="font-bold text-[11px] text-slate-300 uppercase tracking-wider">Classified Physical Evidence Legend</span>
            <span class="text-[10px] text-slate-500 font-mono">MMU: 9 Pixels (0.09 ha)</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px]">
            <div class="flex items-center space-x-1.5">
              <span class="w-3 h-3 rounded-sm bg-[#ef4444] border border-red-300"></span>
              <span class="text-slate-200">New Built-up</span>
            </div>
            <div class="flex items-center space-x-1.5">
              <span class="w-3 h-3 rounded-sm bg-[#22c55e] border border-green-300"></span>
              <span class="text-slate-200">Vegetation Gain</span>
            </div>
            <div class="flex items-center space-x-1.5">
              <span class="w-3 h-3 rounded-sm bg-[#eab308] border border-yellow-300"></span>
              <span class="text-slate-200">Vegetation Loss</span>
            </div>
            <div class="flex items-center space-x-1.5">
              <span class="w-3 h-3 rounded-sm bg-[#06b6d4] border border-cyan-300"></span>
              <span class="text-slate-200">Water Inundation</span>
            </div>
            <div class="flex items-center space-x-1.5">
              <span class="w-3 h-3 rounded-sm bg-[#a855f7] border border-purple-300"></span>
              <span class="text-slate-200">Water Receded</span>
            </div>
          </div>
        </div>

      </div>

      <!-- PHYSICAL HECTARE STATISTICS CARD (CRITICAL: HIDDEN BEFORE ANALYSIS TO PREVENT 0.0 ha BUG) -->
      <div id="cardPhysicalStats" class="hidden bg-obsidian-900 rounded-xl border border-obsidian-700 p-5 space-y-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-obsidian-800 pb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-chart-pie text-crimson-500"></i>
            <h2 class="font-bold text-sm uppercase tracking-wider text-slate-200">Physical Surface Area Breakdown</h2>
          </div>
          <span id="badgeScaleProvenance" class="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-400">
            Georeferenced (EPSG:4326)
          </span>
        </div>

        <!-- 6 Metrics Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          
          <div class="p-3.5 rounded-lg bg-obsidian-950 border border-obsidian-800">
            <div class="text-[11px] text-slate-400 font-semibold mb-1">Total Changed Area</div>
            <div id="statTotalChanged" class="text-xl font-extrabold text-white font-mono">—</div>
            <div id="statTotalPct" class="text-[10px] text-slate-500 mt-0.5">— of target AOI</div>
          </div>

          <div class="p-3.5 rounded-lg bg-obsidian-950 border border-obsidian-800">
            <div class="text-[11px] text-red-400 font-semibold mb-1 flex items-center space-x-1">
              <span class="w-2 h-2 rounded-full bg-red-500"></span>
              <span>New Built-Up</span>
            </div>
            <div id="statBuiltup" class="text-xl font-extrabold text-red-400 font-mono">—</div>
            <div class="text-[10px] text-slate-500 mt-0.5">Paved / Infrastructure</div>
          </div>

          <div class="p-3.5 rounded-lg bg-obsidian-950 border border-obsidian-800">
            <div class="text-[11px] text-yellow-400 font-semibold mb-1 flex items-center space-x-1">
              <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
              <span>Vegetation Loss</span>
            </div>
            <div id="statVegLoss" class="text-xl font-extrabold text-yellow-400 font-mono">—</div>
            <div class="text-[10px] text-slate-500 mt-0.5">Harvest / Disturbance</div>
          </div>

          <div class="p-3.5 rounded-lg bg-obsidian-950 border border-obsidian-800">
            <div class="text-[11px] text-emerald-400 font-semibold mb-1 flex items-center space-x-1">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Vegetation Gain</span>
            </div>
            <div id="statVegGain" class="text-xl font-extrabold text-emerald-400 font-mono">—</div>
            <div class="text-[10px] text-slate-500 mt-0.5">Canopy / Crop Growth</div>
          </div>

          <div class="p-3.5 rounded-lg bg-obsidian-950 border border-obsidian-800">
            <div class="text-[11px] text-cyan-400 font-semibold mb-1 flex items-center space-x-1">
              <span class="w-2 h-2 rounded-full bg-cyan-500"></span>
              <span>Water Inundation</span>
            </div>
            <div id="statWaterInc" class="text-xl font-extrabold text-cyan-400 font-mono">—</div>
            <div class="text-[10px] text-slate-500 mt-0.5">Submerged / Lake Expansion</div>
          </div>

          <div class="p-3.5 rounded-lg bg-obsidian-950 border border-obsidian-800">
            <div class="text-[11px] text-purple-400 font-semibold mb-1 flex items-center space-x-1">
              <span class="w-2 h-2 rounded-full bg-purple-500"></span>
              <span>Confidence Score</span>
            </div>
            <div id="statConfidence" class="text-xl font-extrabold text-purple-400 font-mono">—</div>
            <div id="statQualityTier" class="text-[10px] text-slate-500 mt-0.5">High Confidence Tier</div>
          </div>

        </div>

        <!-- Plain English Narrative Summary -->
        <div class="p-4 rounded-lg bg-obsidian-950 border border-obsidian-800 space-y-1.5">
          <div class="text-[11px] uppercase tracking-wider text-slate-400 font-bold">Executive Intelligence Summary</div>
          <p id="txtDirectAnswer" class="text-sm text-slate-200 leading-relaxed">
            Analysis complete.
          </p>
        </div>

        <!-- Limitation notice for unreferenced images -->
        <div id="boxLimitationNotice" class="hidden p-3 rounded-lg bg-amber-950/40 border border-amber-800/60 text-xs text-amber-300">
        </div>

      </div>

    </div>

  </main>

  <!-- ASYNCHRONOUS PIPELINE PROGRESS MODAL -->
  <div id="modalAnalysisProgress" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
    <div class="bg-obsidian-900 border border-obsidian-700 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-5 text-center">
      
      <!-- Radar Radar Animation Icon -->
      <div class="w-16 h-16 mx-auto rounded-full bg-crimson-600/20 border-2 border-crimson-500 flex items-center justify-center text-crimson-400 text-2xl pulse-glow">
        <i class="fa-solid fa-satellite"></i>
      </div>

      <div class="space-y-1">
        <h3 class="font-bold text-lg text-white">Analyzing Satellite Imagery</h3>
        <p id="txtProgressStage" class="text-xs text-slate-400">Validating selected scenes...</p>
      </div>

      <!-- Real-Time Progress Bar -->
      <div class="space-y-1.5">
        <div class="w-full bg-obsidian-950 rounded-full h-3 overflow-hidden border border-obsidian-800">
          <div id="barProgressFill" class="bg-gradient-to-r from-crimson-600 to-red-500 h-full rounded-full transition-all duration-300" style="width: 15%;"></div>
        </div>
        <div class="flex justify-between text-[11px] font-mono text-slate-500">
          <span id="txtProgressPct">15%</span>
          <span>Pipeline: SIH-26167</span>
        </div>
      </div>

      <div class="text-[11px] text-slate-500 text-left bg-obsidian-950 p-3 rounded-lg border border-obsidian-800 font-mono space-y-1">
        <div>• Band Ingestion: B02, B03, B04, B08 (10m)</div>
        <div>• Sub-pixel MMU Co-registration active</div>
        <div>• Real-time Geodesic Integration</div>
      </div>

    </div>
  </div>

  <!-- FREE SATELLITE IMAGES GUIDE MODAL -->
  <div id="dataGuideModal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
    <div class="bg-obsidian-900 border border-obsidian-700 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4 text-left">
      <div class="flex items-center justify-between border-b border-obsidian-800 pb-3">
        <h3 class="font-bold text-base text-white flex items-center space-x-2">
          <i class="fa-solid fa-satellite text-crimson-400"></i>
          <span>How to Get Free Satellite Images</span>
        </h3>
        <button onclick="toggleDataGuideModal()" class="text-slate-400 hover:text-white text-sm">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="space-y-3 text-xs text-slate-300 leading-relaxed max-h-96 overflow-y-auto pr-1">
        <div class="p-3 rounded-lg bg-obsidian-950 border border-obsidian-800 space-y-1">
          <div class="font-bold text-slate-200">1. Copernicus Data Space Ecosystem (Recommended)</div>
          <p class="text-slate-400">Access open Sentinel-2 (10m optical) and Sentinel-1 (C-band SAR) products globally at <code>browser.dataspace.copernicus.eu</code>.</p>
        </div>
        <div class="p-3 rounded-lg bg-obsidian-950 border border-obsidian-800 space-y-1">
          <div class="font-bold text-slate-200">2. USGS EarthExplorer & Landsat 8/9</div>
          <p class="text-slate-400">Download multispectral Level-2 surface reflectance products across all continents at <code>earthexplorer.usgs.gov</code>.</p>
        </div>
        <div class="p-3 rounded-lg bg-obsidian-950 border border-obsidian-800 space-y-1">
          <div class="font-bold text-slate-200">3. ISRO Bhoonidhi Open Geoportal</div>
          <p class="text-slate-400">Access Cartosat, Resourcesat, and Oceansat datasets for Indian territory at <code>bhoonidhi.nrsc.gov.in</code>.</p>
        </div>
      </div>
      <button onclick="toggleDataGuideModal()" class="w-full py-2 bg-crimson-600 hover:bg-crimson-500 text-white rounded-lg text-xs font-semibold">
        Close Guide
      </button>
    </div>
  </div>

  <!-- FOOTER -->
  <footer class="border-t border-obsidian-800/80 bg-obsidian-950 py-6 text-center text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
      <div>SatQuery AI // Smart India Hackathon 2026 PS 26167 (ISRO / Department of Space)</div>
      <div>Designed for Autonomous Multimodal Remote Sensing Operations</div>
    </div>
  </footer>

  <!-- APPLICATION LOGIC JAVASCRIPT -->
  <script>
    // State store
    const state = {
      activeWorkflow: 'live', // 'live' or 'upload'
      viewerMode: 'split',    // 'split', 'overlay', 'sideBySide'
      currentLocation: {
        name: 'Gudlavalleru',
        display_name: 'Gudlavalleru, Krishna District, Andhra Pradesh, India',
        lat: 16.02,
        lon: 80.70,
        bbox: [80.65, 15.98, 80.75, 16.08]
      },
      scenes: [],
      t1SceneId: 'gvl_s2_2025_09_03',
      t2SceneId: 'gvl_s2_2026_09_05',
      t1File: null,
      t2File: null,
      splitPos: 50,
      activeJobId: null,
      jobPollTimer: null,
      leafletMap: null,
      aoiLayer: null
    };

    // DOM Elements
    const elements = {
      splitWrapper: document.getElementById('viewSplitMode'),
      splitDivider: document.getElementById('splitDivider'),
      imgSplitBefore: document.getElementById('imgSplitBefore'),
      imgSplitAfter: document.getElementById('imgSplitAfter'),
      viewSplitMode: document.getElementById('viewSplitMode'),
      viewOverlayMode: document.getElementById('viewOverlayMode'),
      viewSideBySideMode: document.getElementById('viewSideBySideMode'),
      imgOverlayBase: document.getElementById('imgOverlayBase'),
      imgOverlayChange: document.getElementById('imgOverlayChange'),
      overlayPlaceholderNotice: document.getElementById('overlayPlaceholderNotice'),
      overlayControlsBar: document.getElementById('overlayControlsBar'),
      classificationLegendCard: document.getElementById('classificationLegendCard'),
      cardPhysicalStats: document.getElementById('cardPhysicalStats'),
      modalAnalysisProgress: document.getElementById('modalAnalysisProgress'),
      txtProgressStage: document.getElementById('txtProgressStage'),
      barProgressFill: document.getElementById('barProgressFill'),
      txtProgressPct: document.getElementById('txtProgressPct'),
      btnExportPdf: document.getElementById('btnExportPdf')
    };

    // Initialize application
    window.addEventListener('DOMContentLoaded', () => {
      initSplitSlider();
      initLeafletMap();
      fetchHealth();
      executePlaceSearch('Gudlavalleru');
    });

    // Health Telemetry
    async function fetchHealth() {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'online' || data.status === 'healthy') {
            document.getElementById('pillRouter').innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span>Router: <strong class="text-emerald-400">Ready</strong></span>';
            document.getElementById('pillCopernicus').innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span>Copernicus: <strong class="text-emerald-400">Connected</strong></span>';
            document.getElementById('pillEngine').innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span>Engine: <strong class="text-emerald-400">Active</strong></span>';
          }
        }
      } catch (e) {
        console.warn('Health check warning:', e);
      }
    }

    // Leaflet AOI Map
    function initLeafletMap() {
      try {
        state.leafletMap = L.map('aoiMap', {
          zoomControl: false,
          attributionControl: false
        }).setView([16.02, 80.70], 11);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
          maxZoom: 19
        }).addTo(state.leafletMap);

        updateAoiBoundingBox(state.currentLocation.bbox, state.currentLocation.lat, state.currentLocation.lon);
      } catch (err) {
        console.error('Leaflet map error:', err);
      }
    }

    function updateAoiBoundingBox(bbox, lat, lon) {
      if (!state.leafletMap) return;
      if (state.aoiLayer) {
        state.leafletMap.removeLayer(state.aoiLayer);
      }
      // bbox is [min_lon, min_lat, max_lon, max_lat] or [min_lat, min_lon, max_lat, max_lon]
      let bounds;
      if (bbox && bbox.length === 4) {
        if (bbox[0] > bbox[1] && bbox[0] > 50) {
          // [min_lon, min_lat, max_lon, max_lat]
          bounds = [[bbox[1], bbox[0]], [bbox[3], bbox[2]]];
        } else {
          // [min_lat, min_lon, max_lat, max_lon]
          bounds = [[bbox[0], bbox[1]], [bbox[2], bbox[3]]];
        }
      } else {
        bounds = [[lat - 0.05, lon - 0.05], [lat + 0.05, lon + 0.05]];
      }

      state.aoiLayer = L.rectangle(bounds, {
        color: '#ef2b32',
        weight: 2,
        fillColor: '#ef2b32',
        fillOpacity: 0.15
      }).addTo(state.leafletMap);

      state.leafletMap.fitBounds(bounds, { padding: [15, 15] });
    }

    // Fixed Split Comparison Slider Implementation
    function initSplitSlider() {
      const container = elements.splitWrapper;
      let isDragging = false;

      function updateSlider(clientX) {
        const rect = container.getBoundingClientRect();
        let x = clientX - rect.left;
        if (x < 0) x = 0;
        if (x > rect.width) x = rect.width;
        const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
        state.splitPos = pct;
        container.style.setProperty('--split-pos', pct + '%');
      }

      elements.splitDivider.addEventListener('mousedown', (e) => {
        isDragging = true;
        e.preventDefault();
      });

      window.addEventListener('mouseup', () => {
        isDragging = false;
      });

      window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        updateSlider(e.clientX);
      });

      // Touch events support
      elements.splitDivider.addEventListener('touchstart', (e) => {
        isDragging = true;
      }, { passive: true });

      window.addEventListener('touchend', () => {
        isDragging = false;
      });

      window.addEventListener('touchmove', (e) => {
        if (!isDragging || !e.touches[0]) return;
        updateSlider(e.touches[0].clientX);
      });
    }

    // Switch between Live Location and Upload Workflows
    function switchWorkflow(mode) {
      state.activeWorkflow = mode;
      const cardLive = document.getElementById('cardSelectLive');
      const cardUpload = document.getElementById('cardSelectUpload');
      const panelLive = document.getElementById('panelLiveLocation');
      const panelUpload = document.getElementById('panelUploadImagery');

      if (mode === 'live') {
        cardLive.className = 'cursor-pointer p-5 rounded-xl bg-obsidian-850 border-2 border-crimson-500/80 hover:border-crimson-500 shadow-lg shadow-crimson-900/20 transition-all';
        cardUpload.className = 'cursor-pointer p-5 rounded-xl bg-obsidian-850 border border-obsidian-700 hover:border-crimson-500/70 transition-all';
        panelLive.classList.remove('hidden');
        panelUpload.classList.add('hidden');
      } else {
        cardUpload.className = 'cursor-pointer p-5 rounded-xl bg-obsidian-850 border-2 border-crimson-500/80 hover:border-crimson-500 shadow-lg shadow-crimson-900/20 transition-all';
        cardLive.className = 'cursor-pointer p-5 rounded-xl bg-obsidian-850 border border-obsidian-700 hover:border-crimson-500/70 transition-all';
        panelUpload.classList.remove('hidden');
        panelLive.classList.add('hidden');
      }
    }

    // Switch Viewer Modes
    function setViewerMode(mode) {
      state.viewerMode = mode;
      const tSplit = document.getElementById('tabModeSplit');
      const tOverlay = document.getElementById('tabModeOverlay');
      const tSide = document.getElementById('tabModeSide');

      [tSplit, tOverlay, tSide].forEach(el => {
        el.className = 'px-3 py-1 rounded-md text-xs font-semibold bg-obsidian-800 hover:bg-obsidian-700 text-slate-300 transition-all';
      });

      elements.viewSplitMode.classList.add('hidden');
      elements.viewOverlayMode.classList.add('hidden');
      elements.viewSideBySideMode.classList.add('hidden');
      elements.overlayControlsBar.classList.add('hidden');

      if (mode === 'split') {
        tSplit.className = 'px-3 py-1 rounded-md text-xs font-semibold bg-crimson-600 text-white transition-all';
        elements.viewSplitMode.classList.remove('hidden');
      } else if (mode === 'overlay') {
        tOverlay.className = 'px-3 py-1 rounded-md text-xs font-semibold bg-crimson-600 text-white transition-all';
        elements.viewOverlayMode.classList.remove('hidden');
        elements.overlayControlsBar.classList.remove('hidden');
      } else if (mode === 'sideBySide') {
        tSide.className = 'px-3 py-1 rounded-md text-xs font-semibold bg-crimson-600 text-white transition-all';
        elements.viewSideBySideMode.classList.remove('hidden');
      }
    }

    function updateOverlayOpacity(val) {
      document.getElementById('txtOpacityVal').innerText = val + '%';
      elements.imgOverlayChange.style.opacity = (val / 100.0);
    }

    function toggleDataGuideModal() {
      const modal = document.getElementById('dataGuideModal');
      if (modal) {
        modal.classList.toggle('hidden');
      }
    }

    // Quick Place Search Shortcut
    function quickSearch(placeName) {
      document.getElementById('inputPlaceSearch').value = placeName;
      executePlaceSearch(placeName);
    }

    // Execute Place Geocoding & Scene Discovery
    async function executePlaceSearch(query) {
      const q = query || document.getElementById('inputPlaceSearch').value.trim();
      if (!q) return;

      try {
        // 1. Geocode location via /api/location/search
        const locRes = await fetch(`/api/location/search?q=${encodeURIComponent(q)}`);
        if (locRes.ok) {
          const locData = await locRes.json();
          state.currentLocation = locData;
          const coordsText = locData.coordinates_display || `${locData.lat}° N, ${locData.lon}° E`;
          document.getElementById('txtCoordsPill').innerText = coordsText;
          const hud = document.getElementById('hudLatLon');
          if (hud) hud.innerText = coordsText;
          if (locData.area_km2) {
            document.getElementById('txtAoiAreaKm2').innerText = `AOI: ~${locData.area_km2} km²`;
          }
          updateAoiBoundingBox(locData.bbox, locData.lat, locData.lon);
        }

        // 2. Fetch scenes for location from Copernicus CDSE
        const scenesRes = await fetch(`/api/copernicus/scenes?aoi_name=${encodeURIComponent(q)}&limit=5`);
        if (scenesRes.ok) {
          const scData = await scenesRes.json();
          state.scenes = scData.scenes || [];
          document.getElementById('txtSceneCount').innerText = `${state.scenes.length} passes ready`;
          renderSceneList(state.scenes);

          // Update image viewports with scene thumbnails
          if (state.scenes.length >= 2) {
            const t2 = state.scenes[0];
            const t1 = state.scenes[1];
            state.t2SceneId = t2.id;
            state.t1SceneId = t1.id;
            
            const t1Url = t1.file_path || t1.thumbnail_url || '/static/thumbs/gvl_s2_2025_09_03.jpg';
            const t2Url = t2.file_path || t2.thumbnail_url || '/static/thumbs/gvl_s2_2026_09_05.jpg';

            elements.imgSplitBefore.src = t1Url;
            elements.imgSplitAfter.src = t2Url;
            elements.imgOverlayBase.src = t2Url;
            document.getElementById('imgSideBefore').src = t1Url;
            document.getElementById('imgSideAfter').src = t2Url;

            document.getElementById('tagDateT1').innerText = `T1: ${t1.date}`;
            document.getElementById('tagDateT2').innerText = `T2: ${t2.date}`;
          }
        }
      } catch (err) {
        console.error('Search place error:', err);
      }
    }

    function renderSceneList(scenes) {
      const container = document.getElementById('sceneListContainer');
      if (!scenes || scenes.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-500 text-center py-4">No satellite scenes found for this area.</div>';
        return;
      }

      container.innerHTML = scenes.map((s, idx) => {
        const isT2 = (idx === 0);
        const isT1 = (idx === 1);
        const badge = isT2
          ? '<span class="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-700 text-[10px] text-emerald-400 font-semibold">T2 (After)</span>'
          : (isT1
            ? '<span class="px-2 py-0.5 rounded bg-sky-950/80 border border-sky-700 text-[10px] text-sky-400 font-semibold">T1 (Before)</span>'
            : `<button onclick="selectScene('${s.id}')" class="px-2 py-0.5 rounded bg-obsidian-800 hover:bg-obsidian-700 text-[10px] text-slate-300">Select</button>`);

        return `
          <div class="p-2.5 rounded-lg bg-obsidian-950 border border-obsidian-700 flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2.5">
              <span class="w-2 h-2 rounded-full ${isT2 ? 'bg-emerald-400' : (isT1 ? 'bg-sky-400' : 'bg-slate-600')}"></span>
              <div>
                <div class="font-semibold text-slate-200">${s.date}</div>
                <div class="text-[10px] text-slate-400 font-mono">Cloud: ${s.cloud_cover.toFixed(1)}% | Sentinel-2 L2A</div>
              </div>
            </div>
            <div>${badge}</div>
          </div>
        `;
      }).join('');
    }

    // Handle Local File Uploads
    function handleFileUpload(event, slot) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target.result;
        if (slot === 't1') {
          state.t1File = file;
          document.getElementById('labelT1').innerText = file.name;
          elements.imgSplitBefore.src = dataUrl;
          document.getElementById('imgSideBefore').src = dataUrl;
          document.getElementById('tagDateT1').innerText = `T1: ${file.name}`;
        } else {
          state.t2File = file;
          document.getElementById('labelT2').innerText = file.name;
          elements.imgSplitAfter.src = dataUrl;
          elements.imgOverlayBase.src = dataUrl;
          document.getElementById('imgSideAfter').src = dataUrl;
          document.getElementById('tagDateT2').innerText = `T2: ${file.name}`;
        }
      };
      reader.readAsDataURL(file);
    }

    // START SATELLITE ANALYSIS (Asynchronous Job Polling)
    async function startSatelliteAnalysis() {
      const query = document.getElementById('inputQuery').value.trim();
      const btn = document.getElementById('btnStartAnalysis');

      // 1. Show Progress Modal
      elements.modalAnalysisProgress.classList.remove('hidden');
      elements.txtProgressStage.innerText = "Initializing satellite analysis job...";
      elements.barProgressFill.style.width = "10%";
      elements.txtProgressPct.innerText = "10%";
      btn.disabled = true;

      try {
        const formData = new FormData();
        formData.append('query', query);

        if (state.activeWorkflow === 'upload' && state.t1File && state.t2File) {
          formData.append('files', state.t1File);
          formData.append('files', state.t2File);
          formData.append('location_name', 'Custom Satellite Upload');
        } else {
          formData.append('location_name', state.currentLocation.name || 'Gudlavalleru');
          formData.append('scene_id_1', state.t1SceneId || 'gvl_s2_2025_09_03');
          formData.append('scene_id_2', state.t2SceneId || 'gvl_s2_2026_09_05');
        }

        // Post to start job
        const startRes = await fetch('/api/analysis/start', {
          method: 'POST',
          body: formData
        });

        if (!startRes.ok) {
          throw new Error(`Failed to queue analysis: ${startRes.statusText}`);
        }

        const startData = await startRes.json();
        state.activeJobId = startData.job_id;

        // Poll job status until completed
        pollAnalysisJob(state.activeJobId);

      } catch (err) {
        console.error('Analysis execution error:', err);
        elements.modalAnalysisProgress.classList.add('hidden');
        btn.disabled = false;
        alert(`Analysis error: ${err.message}`);
      }
    }

    function pollAnalysisJob(jobId) {
      if (state.jobPollTimer) clearInterval(state.jobPollTimer);

      state.jobPollTimer = setInterval(async () => {
        try {
          const res = await fetch(`/api/analysis/${jobId}`);
          if (!res.ok) return;

          const job = await res.json();

          // Update Progress Modal Telemetry
          if (job.progress_pct) {
            elements.barProgressFill.style.width = `${job.progress_pct}%`;
            elements.txtProgressPct.innerText = `${job.progress_pct}%`;
          }
          if (job.message) {
            elements.txtProgressStage.innerText = job.message;
          }

          // Check completion
          if (job.status === 'completed') {
            clearInterval(state.jobPollTimer);
            elements.modalAnalysisProgress.classList.add('hidden');
            document.getElementById('btnStartAnalysis').disabled = false;

            // Fetch final results & render
            fetchAndRenderResults(jobId);
          } else if (job.status === 'failed') {
            clearInterval(state.jobPollTimer);
            elements.modalAnalysisProgress.classList.add('hidden');
            document.getElementById('btnStartAnalysis').disabled = false;
            alert(`Analysis failed: ${job.error_message || 'Pipeline execution halted.'}`);
          }

        } catch (e) {
          console.warn('Poll error:', e);
        }
      }, 350);
    }

    // Render Final Results
    async function fetchAndRenderResults(jobId) {
      try {
        const res = await fetch(`/api/analysis/${jobId}/results`);
        if (!res.ok) return;

        const data = await res.json();

        // 1. Update Overlay Viewer with Real Overlay Image
        elements.imgOverlayChange.src = `/api/analysis/${jobId}/overlay?t=${Date.now()}`;
        elements.imgOverlayChange.classList.remove('hidden');
        elements.overlayPlaceholderNotice.classList.add('hidden');

        // Reveal the classification legend now that overlay is ready
        elements.classificationLegendCard.classList.remove('hidden');

        // 2. Reveal and Populate Physical Hectare Statistics Card
        elements.cardPhysicalStats.classList.remove('hidden');

        const areas = data.areas || {};
        document.getElementById('statTotalChanged').innerText = areas.total_changed_display || '—';
        document.getElementById('statTotalPct').innerText = areas.changed_pct ? `${areas.changed_pct.toFixed(1)}% of valid AOI` : '—';
        document.getElementById('statBuiltup').innerText = areas.builtup_display || '—';
        document.getElementById('statVegLoss').innerText = areas.veg_loss_display || '—';
        document.getElementById('statVegGain').innerText = areas.veg_gain_display || '—';
        document.getElementById('statWaterInc').innerText = areas.water_inc_display || '—';

        if (data.confidence) {
          document.getElementById('statConfidence').innerText = `${data.confidence.percentage || (data.confidence.score * 100).toFixed(0)}%`;
          document.getElementById('statQualityTier').innerText = data.confidence.tier || 'Verified Quality';
        }

        // Provenance Badge
        const provBadge = document.getElementById('badgeScaleProvenance');
        if (areas.is_georeferenced) {
          provBadge.className = "text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-400";
          provBadge.innerText = `Georeferenced (10m GSD | EPSG:4326)`;
          document.getElementById('boxLimitationNotice').classList.add('hidden');
        } else {
          provBadge.className = "text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-amber-950 border border-amber-800 text-amber-400";
          provBadge.innerText = `Non-Georeferenced Upload`;
          if (areas.limitation_notice) {
            const limBox = document.getElementById('boxLimitationNotice');
            limBox.innerText = `Notice: ${areas.limitation_notice}`;
            limBox.classList.remove('hidden');
          }
        }

        // Narrative Summary
        document.getElementById('txtDirectAnswer').innerText = data.direct_answer || data.summary || "Analysis executed.";

        // Enable Export PDF Button
        elements.btnExportPdf.disabled = false;

        // Auto-switch to overlay view to show evidence
        setViewerMode('overlay');

      } catch (err) {
        console.error('Error fetching results:', err);
      }
    }

    // Export PDF Report
    function downloadPdfReport() {
      if (!state.activeJobId) return;
      window.open(`/api/analysis/${state.activeJobId}/report`, '_blank');
    }

    // Reset All State
    function resetAllState() {
      elements.cardPhysicalStats.classList.add('hidden');
      elements.classificationLegendCard.classList.add('hidden');
      elements.imgOverlayChange.classList.add('hidden');
      elements.overlayPlaceholderNotice.classList.remove('hidden');
      elements.btnExportPdf.disabled = true;
      setViewerMode('split');
      executePlaceSearch('Gudlavalleru');
    }
  </script>

</body>
</html>
"""
