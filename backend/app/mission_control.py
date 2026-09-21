"""
SatQuery AI — Production-Grade Mission Control Dashboard (PS 26167)
Dominance-Grade Black & Red Defense Intelligence Theme
Integrated with Live Copernicus Data Space Discovery, Explainable Overlays, and Multi-Query Sessions.
"""

MISSION_CONTROL_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SatQuery AI — Autonomous Vision-Language Satellite Intelligence (PS 26167)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            void: {
              950: '#070709',
              900: '#0d0d12',
              850: '#121218',
              800: '#181822',
              700: '#232332',
              600: '#323246'
            },
            crimson: {
              400: '#f87171',
              500: '#ef4444',
              600: '#dc2626',
              700: '#b91c1c',
              800: '#991b1b',
              900: '#7f1d1d',
              950: '#450a0a'
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
      width: 3px;
      background-color: #ef4444;
      cursor: ew-resize;
      z-index: 20;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.8);
    }
    .slider-handle::after {
      content: '< >';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #dc2626;
      color: white;
      font-size: 10px;
      font-weight: 800;
      padding: 4px 6px;
      border-radius: 9999px;
      box-shadow: 0 0 10px rgba(0,0,0,0.8);
      border: 1px solid rgba(255,255,255,0.4);
    }
    /* Smooth custom scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #0d0d12;
    }
    ::-webkit-scrollbar-thumb {
      background: #232332;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #dc2626;
    }
  </style>
</head>
<body class="bg-void-950 text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-crimson-600 selection:text-white">

  <!-- Top Header Navigation -->
  <header class="border-b border-crimson-950/80 bg-void-900/90 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-tr from-crimson-600 to-red-500 flex items-center justify-center shadow-lg shadow-crimson-600/30">
          <i class="fa-solid fa-satellite text-white text-lg"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-red-200 to-crimson-400 bg-clip-text text-transparent">SatQuery AI</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-crimson-950 text-crimson-400 border border-crimson-800 font-mono font-semibold">PS 26167</span>
          </div>
          <p class="text-xs text-slate-400">ISRO / SAC &bull; Multimodal Remote Sensing Operations Assistant</p>
        </div>
      </div>
      
      <div class="flex items-center space-x-3">
        <div class="hidden md:flex items-center space-x-2 text-xs text-slate-400 bg-void-950 px-3 py-1.5 rounded-md border border-void-700">
          <span class="w-2 h-2 rounded-full bg-crimson-500 animate-pulse"></span>
          <span>Agentic Router: <b class="text-crimson-400">Active</b></span>
          <span class="text-slate-600">|</span>
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Copernicus CDSE: <b class="text-emerald-400">Online</b></span>
        </div>
        <button onclick="openDataModal()" class="inline-flex items-center space-x-1.5 bg-void-850 hover:bg-void-800 text-slate-300 hover:text-white text-xs font-medium px-3 py-2 rounded-lg border border-void-700 hover:border-crimson-600 transition shadow-sm">
          <i class="fa-solid fa-circle-question text-crimson-400"></i>
          <span>How to Get Free Data</span>
        </button>
        <button onclick="openTraceModal()" id="headerTraceBtn" class="inline-flex items-center space-x-1.5 bg-void-850 hover:bg-void-800 text-slate-300 hover:text-white text-xs font-medium px-3 py-2 rounded-lg border border-void-700 hover:border-crimson-600 transition shadow-sm">
          <i class="fa-solid fa-microchip text-crimson-400"></i>
          <span>Audit Trace</span>
        </button>
        <button onclick="downloadLatestReport()" id="headerDownloadBtn" disabled class="disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center space-x-2 bg-gradient-to-r from-crimson-700 to-red-600 hover:from-crimson-600 hover:to-red-500 text-white text-xs font-medium px-3.5 py-2 rounded-lg transition shadow-md shadow-crimson-900/30">
          <i class="fa-solid fa-file-pdf"></i>
          <span>Download Mission PDF</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 grid grid-cols-1 lg:grid-cols-12 gap-5">

    <!-- Hero Operational Banner -->
    <div class="lg:col-span-12 bg-void-900 border border-crimson-950 text-slate-200 text-xs px-4 py-3 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-lg bg-crimson-950/80 border border-crimson-800 text-crimson-400 flex items-center justify-center flex-shrink-0">
          <i class="fa-solid fa-satellite-dish text-sm"></i>
        </div>
        <div>
          <b class="text-white text-sm">SatQuery AI &mdash; Satellite Intelligence, Simplified.</b>
          <p class="text-[11px] text-slate-400">Ask questions about satellite images in simple English. Get verified answers, interactive maps, and audit-ready PDF reports.</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-[10px] bg-void-950 text-crimson-400 px-2.5 py-1 rounded-full border border-crimson-900 font-mono font-semibold">
          Sentinel-2 &bull; Sentinel-1 SAR &bull; Cartosat &bull; LEVIR-CD
        </span>
      </div>
    </div>

    <!-- Left Controls Panel (5 Cols) -->
    <div class="lg:col-span-5 space-y-4 flex flex-col">

      <!-- Navigation Mode Tabs -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-1.5 flex gap-1 shadow-sm">
        <button onclick="switchModeTab('demo')" id="tabBtnDemo" class="flex-1 py-2 px-2.5 rounded-lg text-xs font-semibold bg-crimson-600 text-white transition flex items-center justify-center space-x-1.5 shadow">
          <i class="fa-solid fa-bolt text-[11px]"></i>
          <span>1-Click Scenarios</span>
        </button>
        <button onclick="switchModeTab('copernicus')" id="tabBtnCopernicus" class="flex-1 py-2 px-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center justify-center space-x-1.5">
          <i class="fa-solid fa-globe text-[11px]"></i>
          <span>Live Copernicus</span>
        </button>
        <button onclick="switchModeTab('upload')" id="tabBtnUpload" class="flex-1 py-2 px-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center justify-center space-x-1.5">
          <i class="fa-solid fa-cloud-arrow-up text-[11px]"></i>
          <span>Upload Image</span>
        </button>
      </div>

      <!-- Tab 1: 1-Click Demo Scenarios -->
      <div id="tabContentDemo" class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <i class="fa-solid fa-star text-crimson-500"></i>
            <span>Featured Demo Scenarios</span>
          </h2>
          <span class="text-[10px] text-crimson-400 font-mono">Instant Run</span>
        </div>

        <!-- State-Wide Andhra Pradesh Location Bar -->
        <div class="p-2.5 rounded-lg bg-void-850 border border-crimson-900/60 space-y-2">
          <div class="flex items-center justify-between text-[11px] font-semibold text-slate-200">
            <span class="flex items-center space-x-1.5">
              <i class="fa-solid fa-map-location-dot text-crimson-400"></i>
              <span>Andhra Pradesh State-Wide Coverage</span>
            </span>
            <span class="text-[9px] bg-crimson-950 text-crimson-300 px-1.5 py-0.5 rounded font-mono font-bold border border-crimson-900">11 Regions &bull; 2025 vs 2026</span>
          </div>

          <div class="flex gap-1.5">
            <input type="text" id="dashboardLocSearch" value="Gudlavalleru" placeholder="Search AP (e.g. Gudlavalleru, Vijayawada, Vizag, Tirupati)..." class="flex-1 bg-void-950 border border-void-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500" onkeydown="if(event.key==='Enter') searchLocationDashboard()">
            <button onclick="searchLocationDashboard()" class="bg-crimson-600 hover:bg-crimson-500 text-white text-xs px-3 py-1.5 rounded font-semibold transition flex items-center space-x-1 shadow">
              <i class="fa-solid fa-magnifying-glass text-[10px]"></i>
              <span>Locate</span>
            </button>
          </div>

          <!-- Quick City Pills -->
          <div class="flex flex-wrap gap-1 pt-0.5">
            <button onclick="selectApCity('gudlavalleru')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Gudlavalleru</button>
            <button onclick="selectApCity('avanigadda')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Avanigadda</button>
            <button onclick="selectApCity('vijayawada')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Vijayawada</button>
            <button onclick="selectApCity('amaravati')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Amaravati</button>
            <button onclick="selectApCity('visakhapatnam')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Visakhapatnam</button>
            <button onclick="selectApCity('tirupati')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Tirupati</button>
            <button onclick="selectApCity('kurnool')" class="text-[9px] bg-void-950 hover:bg-crimson-950/60 border border-crimson-900/60 hover:border-crimson-500 text-slate-300 hover:text-white px-2 py-0.5 rounded transition">Kurnool</button>
            <button onclick="selectApCity('ap_state_overview')" class="text-[9px] bg-crimson-950/80 hover:bg-crimson-900 border border-crimson-600 text-crimson-200 px-2 py-0.5 rounded transition font-bold">Entire AP</button>
          </div>

          <div class="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-void-800">
            <span id="dashboardAoiCoords" class="text-crimson-400 font-mono font-medium">AOI: 16.02°N, 80.70°E (Gudlavalleru)</span>
            <span class="text-emerald-400 font-mono text-[9px] bg-emerald-950/60 border border-emerald-800/60 px-1.5 py-0.5 rounded">Sentinel-2 2025 vs 2026</span>
          </div>
        </div>

        <div class="space-y-2 max-h-[340px] overflow-y-auto pr-1">
          <!-- Scenario 1: Gudlavalleru Urban Growth -->
          <button onclick="selectApCity('gudlavalleru')" id="btn_ap_gudlavalleru" class="scenario-btn w-full text-left p-2.5 rounded-lg border border-crimson-600 bg-void-850 hover:border-crimson-400 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-crimson-300 flex items-center space-x-1.5">
                <i class="fa-solid fa-building text-crimson-400"></i>
                <span>1. Gudlavalleru &mdash; Urban Growth (2025 vs 2026)</span>
              </span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-crimson-950 text-crimson-400 font-mono font-semibold">Demo 1</span>
            </div>
            <p class="text-[11px] text-slate-300 mt-1">Krishna delta corridor & educational campus. Detects +42.8 ha new built-up expansion.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
              <span class="text-crimson-400 font-bold">Sentinel-2 L2A</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span>16.02°N, 80.70°E</span>
            </div>
          </button>

          <!-- Scenario 2: Visakhapatnam Coastal Port -->
          <button onclick="loadScenario('scenario_4_coastal')" id="btn_scenario_4_coastal" class="scenario-btn w-full text-left p-2.5 rounded-lg border border-void-800 bg-void-950 hover:border-crimson-500 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-200">2. Visakhapatnam &mdash; Coastal Port Sprawl</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-void-800 text-slate-300 font-mono">Demo 2</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Deepwater port 2023 vs 2024. Maps breakwater extensions & container yard paving.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>Sentinel-2 Bi-Temporal</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span class="text-crimson-400">Vizag Port</span>
            </div>
          </button>

          <!-- Scenario 3: Godavari Flood Inundation -->
          <button onclick="loadScenario('scenario_1_flood')" id="btn_scenario_1_flood" class="scenario-btn w-full text-left p-2.5 rounded-lg border border-void-800 bg-void-950 hover:border-crimson-500 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-200">3. Godavari Basin &mdash; Flood & Inundation</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-void-800 text-slate-300 font-mono">Demo 3</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Optical flood scene over Godavari basin. Delineates inundated agricultural parcels.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>Sentinel-2 L2A</span>
              <span>&bull;</span>
              <span>10m GSD</span>
              <span>&bull;</span>
              <span class="text-crimson-400">Flood Mask</span>
            </div>
          </button>

          <!-- Scenario 4: Optical-SAR Cloud Penetration -->
          <button onclick="loadScenario('scenario_3_optical_sar')" id="btn_scenario_3_optical_sar" class="scenario-btn w-full text-left p-2.5 rounded-lg border border-void-800 bg-void-950 hover:border-crimson-500 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-200">4. Optical-SAR &mdash; Cloud Penetration</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-950 text-purple-300 font-mono">Optical + SAR</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Pierces 82% monsoon clouds using C-band radar backscatter to isolate storage tanks.</p>
            <div class="mt-1.5 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
              <span>Cartosat + Sentinel-1</span>
              <span>&bull;</span>
              <span>10m/0.65m GSD</span>
            </div>
          </button>

          <!-- Today's Live Feed -->
          <button onclick="loadScenario('scenario_today_near_real_time')" id="btn_scenario_today_near_real_time" class="scenario-btn w-full text-left p-2.5 rounded-lg border border-void-800 bg-void-950 hover:border-emerald-500 transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-emerald-400 flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Today's Operational Surveillance Feed</span>
              </span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono">NRT Stream</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Direct Copernicus Data Space ingestion pipeline feed. Automated anomaly detection.</p>
          </button>
        </div>
      </div>

      <!-- Tab 2: Live Copernicus Place Search -->
      <div id="tabContentCopernicus" class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3 hidden">
        <div class="flex items-center justify-between">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-satellite text-crimson-400"></i>
            <span>Live Copernicus Sentinel-2 Discovery</span>
          </h2>
          <span class="text-[10px] text-emerald-400 font-mono bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-900">CDSE OData API</span>
        </div>

        <div class="space-y-2">
          <div class="flex gap-1.5">
            <input type="text" id="copernicusPlaceInput" value="Vijayawada" placeholder="Enter ANY place in India or worldwide..." class="flex-1 bg-void-950 border border-void-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500" onkeydown="if(event.key==='Enter') executeCopernicusSearch()">
            <button onclick="executeCopernicusSearch()" id="btnCopernicusSearch" class="bg-crimson-600 hover:bg-crimson-500 text-white text-xs px-3.5 py-1.5 rounded font-semibold transition flex items-center space-x-1.5 shadow">
              <i class="fa-solid fa-magnifying-glass text-[10px]"></i>
              <span>Fetch Scenes</span>
            </button>
          </div>

          <div class="flex items-center justify-between text-[11px] text-slate-400 px-1">
            <span>Max Cloud Cover: <b id="cloudCoverVal" class="text-crimson-400">20%</b></span>
            <input type="range" id="cloudCoverSlider" min="5" max="60" value="20" class="w-32 accent-crimson-500 cursor-pointer" oninput="document.getElementById('cloudCoverVal').innerText = this.value + '%'">
          </div>

          <!-- Copernicus Live Results Container -->
          <div id="copernicusResultsList" class="space-y-2 max-h-[300px] overflow-y-auto pr-1 pt-1">
            <div class="text-center py-6 text-xs text-slate-500">
              Click <b>Fetch Scenes</b> to discover live Sentinel-2 acquisitions for your selected location.
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 3: Upload Custom Images -->
      <div id="tabContentUpload" class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3 hidden">
        <div class="flex items-center justify-between">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-upload text-crimson-400"></i>
            <span>Upload Satellite Images</span>
          </h2>
          <button type="button" onclick="openDataModal()" class="text-[10px] text-crimson-400 hover:underline">Where to get images?</button>
        </div>

        <div class="border-2 border-dashed border-void-700 hover:border-crimson-500 rounded-lg p-5 text-center cursor-pointer transition bg-void-950/60" onclick="document.getElementById('fileInput').click()">
          <input type="file" id="fileInput" multiple accept=".tif,.tiff,.png,.jpg,.jpeg" class="hidden" onchange="handleFileSelect(event)">
          <i class="fa-solid fa-cloud-arrow-up text-crimson-500 text-2xl mb-1.5"></i>
          <p class="text-xs text-slate-200 font-medium" id="uploadLabel">Click or drag & drop 1 or 2 files</p>
          <p class="text-[10px] text-slate-500 mt-0.5">Supports GeoTIFF / PNG &bull; Single, Before/After Pair, or Optical+SAR</p>
        </div>
      </div>

      <!-- Natural Language Query Card -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
            Natural Language Query
          </label>
          <div class="relative">
            <textarea id="queryInput" rows="3" class="w-full bg-void-950 border border-void-700 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 resize-none font-medium" placeholder="E.g. What changed between 2025 and 2026 in this area?"></textarea>
            <div class="absolute right-2.5 bottom-2.5 text-[10px] text-slate-500 font-mono">
              Plain English &bull; Auto-Routed
            </div>
          </div>
        </div>

        <!-- Notification Banner -->
        <div id="toastNotice" class="hidden p-2 rounded-lg bg-void-950 border border-crimson-700/80 text-crimson-200 text-xs font-medium"></div>

        <!-- Suggestion Pills -->
        <div class="flex flex-wrap gap-1.5">
          <button onclick="setQuery('What changed between 2025 and 2026 in this area?')" class="text-[10px] bg-void-950 border border-crimson-900/80 hover:border-crimson-500 px-2.5 py-1 rounded text-crimson-300 transition">🔄 What changed here?</button>
          <button onclick="setQuery('Where are the buildings in this image?')" class="text-[10px] bg-void-950 border border-void-700 hover:border-slate-400 px-2.5 py-1 rounded text-slate-300 transition">🏢 Where are buildings?</button>
          <button onclick="setQuery('Show me the water bodies.')" class="text-[10px] bg-void-950 border border-void-700 hover:border-slate-400 px-2.5 py-1 rounded text-slate-300 transition">💧 Show water bodies</button>
          <button onclick="setQuery('Identify the submerged agricultural parcels and highlight their spatial boundaries.')" class="text-[10px] bg-void-950 border border-void-700 hover:border-slate-400 px-2.5 py-1 rounded text-slate-300 transition">🌾 Submerged farmlands</button>
        </div>

        <!-- Execute Action Button -->
        <button onclick="executeAnalysis()" id="executeBtn" class="w-full bg-gradient-to-r from-crimson-700 to-red-600 hover:from-crimson-600 hover:to-red-500 text-white font-semibold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-crimson-900/40">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
          <span>Analyze Satellite Images</span>
        </button>
      </div>

    </div>

    <!-- Right Visualization & Result Panel (7 Cols) -->
    <div class="lg:col-span-7 space-y-4">

      <!-- Viewport Card with Layer Toggles & Explainable Legend -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm">
        <div class="flex items-center justify-between mb-2.5">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Satellite Viewport</span>
            <span id="detectedBadge" class="hidden text-[10px] px-2 py-0.5 rounded font-mono font-medium bg-crimson-950 text-crimson-400 border border-crimson-800">
              Task: Auto
            </span>
          </div>

          <!-- Layer View Buttons -->
          <div class="flex items-center space-x-1 bg-void-950 p-1 rounded-md border border-void-700 text-xs">
            <button onclick="setViewMode('base')" id="btnViewBase" class="px-2.5 py-1 rounded bg-crimson-600 text-white font-medium text-[11px] transition">Base</button>
            <button onclick="setViewMode('overlay')" id="btnViewOverlay" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition">Evidence Overlay</button>
            <button onclick="setViewMode('split')" id="btnViewSplit" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition">Split Comparison</button>
          </div>
        </div>

        <!-- Interactive Canvas -->
        <div class="relative w-full h-80 bg-black rounded-lg border border-void-800 overflow-hidden flex items-center justify-center">
          <img id="viewerBaseImg" src="/static/thumbs/gvl_s2_2026_09_05.jpg" alt="Base Satellite View" class="absolute inset-0 w-full h-full object-contain">
          
          <img id="viewerOverlayImg" src="" alt="Evidence Overlay" class="absolute inset-0 w-full h-full object-contain hidden opacity-90 transition-opacity">

          <!-- Real-Time Tactical Coordinates HUD Overlay -->
          <div id="viewerCoordsOverlay" class="absolute top-2.5 left-2.5 bg-void-950/90 border border-crimson-600/70 rounded-md px-2.5 py-1.5 text-[11px] font-mono backdrop-blur-md shadow-lg z-20 pointer-events-none flex flex-col space-y-0.5">
            <div class="flex items-center space-x-1.5 text-crimson-400 font-bold tracking-wider uppercase text-[10px]">
              <i class="fa-solid fa-crosshairs animate-pulse"></i>
              <span id="hudLocationName">GUDLAVALLERU, AP</span>
            </div>
            <div class="text-slate-200 font-semibold tracking-wide flex items-center space-x-1 text-[11px]">
              <span class="text-slate-400 text-[10px]">COORDS:</span>
              <span id="hudLatLon" class="text-emerald-400 font-bold">16.0200° N, 80.7000° E</span>
            </div>
            <div class="text-[9px] text-slate-400">
              <span>BBOX:</span> <span id="hudBbox" class="text-slate-300">[15.98, 80.65, 16.08, 80.75]</span>
            </div>
          </div>

          <!-- Split Screen Slider Container -->
          <div id="splitContainer" class="absolute inset-0 hidden pointer-events-none">
            <div id="splitClip" class="absolute inset-0 overflow-hidden w-1/2 border-r-2 border-crimson-500 shadow-2xl">
              <img id="viewerSplitImg" src="/static/thumbs/gvl_s2_2025_09_03.jpg" class="absolute inset-0 w-full h-full object-contain max-w-none">
            </div>
          </div>

          <!-- Explainable Map Legend (Floating on Viewport) -->
          <div id="mapLegend" class="absolute bottom-3 left-3 bg-void-950/95 border border-crimson-900/70 rounded-lg p-2.5 text-[10px] space-y-1 backdrop-blur shadow-2xl z-20">
            <span class="font-bold text-slate-200 block border-b border-void-700 pb-0.5 uppercase tracking-wider text-[9px] flex items-center space-x-1">
              <i class="fa-solid fa-layer-group text-crimson-400 text-[8px]"></i>
              <span>Explainable Change Legend</span>
            </span>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm shadow-red-500/50"></span><span class="text-slate-300">New Built-up & Roads</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50"></span><span class="text-slate-300">Vegetation / Canopy Growth</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/50"></span><span class="text-slate-300">Water Surface Changes</span></div>
          </div>

          <!-- Loading Spinner -->
          <div id="loadingOverlay" class="absolute inset-0 bg-void-950/85 backdrop-blur-sm flex flex-col items-center justify-center space-y-2 hidden z-30">
            <i class="fa-solid fa-circle-notch fa-spin text-crimson-500 text-3xl"></i>
            <span class="text-xs text-slate-200 font-medium animate-pulse" id="loadingStatusText">Analyzing satellite imagery and preparing answer...</span>
          </div>
        </div>

        <!-- Viewport Metadata Footer -->
        <div class="mt-2 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400 px-1 gap-1 border-t border-void-800 pt-2">
          <div class="flex items-center space-x-1.5 overflow-hidden text-ellipsis whitespace-nowrap">
            <span class="text-slate-500 font-semibold uppercase text-[10px]">Data Source:</span>
            <span id="sceneDataSource" class="text-crimson-300 font-medium">Sentinel-2 L2A MSI, Gudlavalleru, AP (2025 vs 2026)</span>
          </div>
          <div class="flex items-center space-x-2 text-slate-400 font-mono text-[10px]">
            <span id="sceneCoordinatesBadge" class="text-crimson-400 font-bold bg-crimson-950/60 px-2 py-0.5 rounded border border-crimson-900/60">LAT: 16.0200° N • LON: 80.7000° E</span>
            <span>&bull;</span>
            <span id="sceneDimensions">512 x 512 px</span>
            <span>&bull;</span>
            <span id="sceneResolution">10 m GSD</span>
            <span>&bull;</span>
            <span id="sceneCRS">EPSG:4326 (WGS84)</span>
          </div>
        </div>
      </div>

      <!-- Direct Answer & Multi-Query Session Card -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <i class="fa-solid fa-clipboard-check text-crimson-400"></i>
            <span>Direct Answer</span>
          </h3>
          <div class="flex items-center space-x-2">
            <span class="text-[11px] text-slate-400">Confidence:</span>
            <div class="w-24 bg-void-950 rounded-full h-2 overflow-hidden border border-void-700">
              <div id="confidenceBar" class="bg-gradient-to-r from-red-600 to-emerald-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
            </div>
            <span id="confidenceValue" class="text-xs font-mono font-bold text-crimson-400">--%</span>
          </div>
        </div>

        <!-- Confidence Calibration Explanation Box -->
        <div id="confidenceReasonBox" class="hidden p-2 rounded bg-void-950 border border-void-700 text-[11px] text-slate-300">
          <i class="fa-solid fa-shield-halved text-crimson-400 mr-1.5"></i>
          <span id="confidenceReasonText">Confidence calibrated using remote sensing edge heuristics.</span>
        </div>

        <div id="answerText" class="p-3 bg-void-950 border border-void-700 rounded-lg text-xs leading-relaxed text-slate-200">
          Select any scenario or location on the left, then click <b>Analyze Satellite Images</b>.
        </div>

        <!-- Key Observations Bullets -->
        <div id="bulletContainer" class="hidden space-y-1 pt-0.5">
          <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Key Observations & Summary</span>
          <ul id="bulletList" class="text-[11px] text-slate-300 space-y-1 list-disc list-inside"></ul>
        </div>

        <!-- Multi-Query Interactive Session Box -->
        <div class="border-t border-void-800 pt-2.5">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
              <i class="fa-solid fa-comments text-crimson-400"></i>
              <span>Multi-Query Session Thread</span>
            </span>
            <span id="sessionActiveBadge" class="hidden text-[9px] text-emerald-400 font-mono bg-emerald-950 px-1.5 py-0.2 rounded">Imagery Cached</span>
          </div>
          <div id="chatHistoryBox" class="space-y-1.5 max-h-36 overflow-y-auto mb-2 text-xs">
            <!-- Dynamically populated multi-query thread -->
          </div>
          <div class="flex gap-1.5">
            <input type="text" id="followUpQueryInput" placeholder="Ask another question about this imagery (e.g. 'Where are the buildings?')..." class="flex-1 bg-void-950 border border-void-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500" onkeydown="if(event.key==='Enter') executeFollowUpQuery()">
            <button onclick="executeFollowUpQuery()" id="btnFollowUp" class="bg-void-800 hover:bg-crimson-600 text-slate-200 hover:text-white px-3 py-1.5 rounded text-xs font-semibold transition border border-void-700 hover:border-crimson-500">
              Ask
            </button>
          </div>
        </div>
      </div>

      <!-- Auditable Execution Trace Accordion -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm">
        <button onclick="toggleTraceAccordion()" class="w-full flex items-center justify-between text-left">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-microchip text-crimson-400 text-xs"></i>
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300">Auditable Execution Trace</span>
            <span id="traceIdBadge" class="text-[10px] font-mono text-slate-500">ID: none</span>
          </div>
          <i id="traceChevron" class="fa-solid fa-chevron-down text-slate-400 text-xs transition-transform"></i>
        </button>

        <div id="traceContent" class="hidden mt-3 pt-3 border-t border-void-800 text-xs space-y-2.5 font-mono">
          <div class="bg-void-950 p-2.5 rounded border border-void-800 text-[11px] space-y-1">
            <div class="text-slate-400"><b class="text-slate-200">Router Decision:</b> <span id="traceRouterReasoning" class="text-crimson-300">Awaiting execution...</span></div>
            <div class="text-slate-400"><b class="text-slate-200">Data Source:</b> <span id="traceDataSource" class="text-slate-300">Sentinel-2 L2A State Archive</span></div>
            <div class="text-slate-400"><b class="text-slate-200">Latency:</b> <span id="traceLatency" class="text-emerald-400">-- ms</span></div>
          </div>

          <div>
            <span class="text-[10px] uppercase text-slate-400 font-sans font-bold">Specialist Tool Telemetry</span>
            <div id="traceToolsList" class="mt-1.5 space-y-1.5 font-sans">
              <!-- Rendered dynamically -->
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>

  <!-- Modal 1: How to Get Free Satellite Images -->
  <div id="dataGuideModal" class="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-void-900 border border-void-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-void-800 pb-3">
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-lg bg-crimson-950/80 border border-crimson-800 text-crimson-400 flex items-center justify-center">
            <i class="fa-solid fa-satellite-dish text-base"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-white">How to Get Free Satellite Images</h3>
            <p class="text-xs text-slate-400">Official Open Earth Observation Sources for SatQuery AI</p>
          </div>
        </div>
        <button onclick="closeDataModal()" class="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-void-800 transition">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <div class="space-y-2.5">
        <h4 class="text-xs font-bold uppercase tracking-wider text-crimson-400">1. Free Satellite Portals</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">Copernicus Browser (ESA)</span>
              <a href="https://browser.dataspace.copernicus.eu" target="_blank" rel="noopener noreferrer" class="text-[10px] text-crimson-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">Sentinel-2 (10m optical) & Sentinel-1 (radar). Free worldwide, updated every 5 days.</p>
            <span class="text-[9px] text-emerald-400 font-mono font-semibold">Recommended for SIH Demo</span>
          </div>

          <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">USGS EarthExplorer</span>
              <a href="https://earthexplorer.usgs.gov" target="_blank" rel="noopener noreferrer" class="text-[10px] text-crimson-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">Landsat 8 & 9 (30m optical). 50+ years archive of Earth surface changes.</p>
            <span class="text-[9px] text-slate-400 font-mono font-semibold">Global Open Archive</span>
          </div>

          <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">ISRO Bhoovikram / Bhuvan</span>
              <a href="https://bhuvan.nrsc.gov.in" target="_blank" rel="noopener noreferrer" class="text-[10px] text-crimson-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">Indian national geospatial portal. Open datasets for Indian land & coastal regions.</p>
            <span class="text-[9px] text-amber-400 font-mono font-semibold">ISRO Open Data</span>
          </div>

          <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200">NASA Earthdata Search</span>
              <a href="https://search.earthdata.nasa.gov" target="_blank" rel="noopener noreferrer" class="text-[10px] text-crimson-400 hover:underline flex items-center space-x-1">
                <span>Open Portal</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
              </a>
            </div>
            <p class="text-[11px] text-slate-400">MODIS, VIIRS, and surface reflectance data for disaster & climate monitoring.</p>
            <span class="text-[9px] text-purple-400 font-mono font-semibold">NASA Open Access</span>
          </div>
        </div>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold uppercase tracking-wider text-crimson-400">2. Simple 6-Step Download Guide (2 Minutes)</h4>
        <ol class="text-xs text-slate-300 space-y-2 list-decimal list-inside bg-void-950 p-3.5 rounded-lg border border-void-800">
          <li><b class="text-white">Open Copernicus Browser:</b> Navigate to <a href="https://browser.dataspace.copernicus.eu" target="_blank" class="text-crimson-400 underline">browser.dataspace.copernicus.eu</a>.</li>
          <li><b class="text-white">Search your place:</b> Type any city or place (e.g. <i>Vijayawada</i>, <i>Gudlavalleru</i>, or any region).</li>
          <li><b class="text-white">Choose Sentinel-2 L2A:</b> Select <i>True Color RGB</i> with cloud cover under 20%.</li>
          <li><b class="text-white">Download:</b> Click the Download button on the right -> Choose <i>Analytical (GeoTIFF)</i> or <i>High-Res Image (PNG/JPG)</i>.</li>
          <li><b class="text-white">Upload to SatQuery AI:</b> Drag & drop the file into the upload box on the left (or select 2 images for Before & After change detection).</li>
          <li><b class="text-white">Ask in Plain English:</b> Type queries like <i>"What changed here between 2025 and 2026?"</i> or <i>"Where are the buildings?"</i> and click <b>Analyze Satellite Images</b>!</li>
        </ol>
      </div>

      <div class="flex justify-end pt-1">
        <button onclick="closeDataModal()" class="bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow">
          Got it, Close Guide
        </button>
      </div>
    </div>
  </div>

  <!-- Modal 2: Auditable Execution Trace (JSON Viewer) -->
  <div id="traceModal" class="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-void-900 border border-void-700 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-void-800 pb-3">
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-lg bg-crimson-950/80 border border-crimson-800 text-crimson-400 flex items-center justify-center">
            <i class="fa-solid fa-code text-sm"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-white">Auditable Execution Trace Telemetry</h3>
            <p class="text-xs text-slate-400 font-mono" id="modalTraceId">Trace ID: none</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="copyTraceJson()" class="text-xs bg-void-800 hover:bg-void-700 text-slate-200 px-3 py-1.5 rounded border border-void-700 transition">
            <i class="fa-solid fa-copy mr-1"></i> Copy JSON
          </button>
          <button onclick="closeTraceModal()" class="text-slate-400 hover:text-white p-1 rounded hover:bg-void-800 transition">
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>
      </div>
      <pre id="traceJsonViewer" class="bg-void-950 border border-void-800 rounded-lg p-3.5 text-[11px] text-emerald-400 font-mono max-h-[60vh] overflow-auto whitespace-pre-wrap leading-relaxed"></pre>
    </div>
  </div>

  <!-- Script for Frontend Logic -->
  <script>
    let activeScenarioId = 'scenario_gudlavalleru_change';
    let selectedFiles = [];
    let currentResponse = null;
    let viewMode = 'base';
    let activeSceneIds = 'gvl_s2_2025_09_03,gvl_s2_2026_09_05';
    let activeAnalysisMode = 'change';
    let currentSessionTraceId = null;
    let sessionHistory = [];

    const SCENARIOS_METADATA = {
      'scenario_1_flood': {
        name: 'Godavari Basin Flood & Inundation',
        sensor: 'Sentinel-2 L2A (MSI)',
        coords: '16.8900°N, 81.7900°E',
        bbox: '[16.50, 81.40, 17.20, 82.10]',
        date: '2023-07-28',
        area: 'Godavari River Basin, AP/Telangana, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326 (WGS84)',
        source: 'Copernicus Open Access Hub / ESA Sentinel-2 L2A',
        image: '/static/demo_scenarios/scenario_1_flood/image1.png',
        query: 'Identify the submerged agricultural parcels and highlight their spatial boundaries.'
      },
      'scenario_2_urban': {
        name: 'Bi-Temporal Urban Expansion',
        sensor: 'High-Res Optical Satellite (LEVIR-CD Benchmark)',
        coords: '39.9042°N, 116.4074°E',
        bbox: '[39.85, 116.35, 39.95, 116.45]',
        date: '2022-04-12 (T1) vs. 2024-05-18 (T2)',
        area: 'Suburban Industrial Development Zone',
        resolution: '0.5 m GSD',
        crs: 'EPSG:4326 (WGS84)',
        source: 'LEVIR-CD Large-Scale Change Detection Archive',
        image: '/static/demo_scenarios/scenario_2_urban/t2.png',
        split_image: '/static/demo_scenarios/scenario_2_urban/t1.png',
        query: 'What major infrastructure changes occurred between these two acquisition dates?'
      },
      'scenario_3_optical_sar': {
        name: 'All-Weather Fusion: Cloud Penetration (Cartosat + RISAT / Sentinel-1)',
        sensor: 'Cartosat-2S Optical + Sentinel-1 C-band SAR',
        coords: '17.6868°N, 83.2185°E',
        bbox: '[17.62, 83.15, 17.75, 83.32]',
        date: '2023-08-20 (Co-registered window)',
        area: 'Coastal Industrial Port & Oil Storage Terminal',
        resolution: 'Optical 0.65m / SAR 10m GSD',
        crs: 'EPSG:4326 (WGS84)',
        source: 'ISRO SAC / ESA Sentinel-1 GRD SAR + Optical Archive',
        image: '/static/demo_scenarios/scenario_3_optical_sar/optical.png',
        query: 'Penetrate cloud cover to map industrial storage tanks and coastal water bodies.'
      },
      'scenario_4_coastal': {
        name: 'Visakhapatnam Coastal Port Sprawl',
        sensor: 'Sentinel-2 L2A MSI',
        coords: '17.6900°N, 83.2200°E',
        bbox: '[17.62, 83.15, 17.75, 83.32]',
        date: '2023-02-15 (T1) vs. 2024-09-05 (T2)',
        area: 'Visakhapatnam Port & Coastal Corridor, AP, India',
        resolution: '10 m GSD',
        crs: 'EPSG:4326 (WGS84)',
        source: 'Copernicus Open Access Hub / ESA Sentinel-2 L2A',
        image: '/static/demo_scenarios/scenario_4_coastal/t2.png',
        split_image: '/static/demo_scenarios/scenario_4_coastal/t1.png',
        query: 'What new coastal infrastructure or breakwater structures were constructed between T1 and T2?'
      },
      'scenario_today_near_real_time': {
        name: "Today's Operational Surveillance Feed (Near-Real-Time Stream)",
        sensor: 'Sentinel-2 L2A MSI',
        coords: '16.0200°N, 80.7000°E',
        bbox: '[15.98, 80.65, 16.08, 80.75]',
        date: '2026-09-22 (Acquired & Ingested Today)',
        area: 'National Space Operational Surveillance Corridor',
        resolution: '10 m GSD',
        crs: 'EPSG:4326 (WGS84)',
        source: 'Copernicus Data Space Ecosystem (Direct Near-Real-Time Stream)',
        image: '/static/latest/latest_scene.png',
        query: 'Detect recent surface changes, water inundation, and newly emerged infrastructure.'
      }
    };

    const AP_SCENARIOS_CATALOG = {
      'gudlavalleru': {
        name: 'Gudlavalleru, Krishna District, AP',
        coords: '16.0200°N, 80.7000°E',
        bbox: 'BBox: [15.98, 80.65, 16.08, 80.75]',
        feature: 'Krishna Delta, Academic Campus, Agricultural Grid',
        date: '2025-09-03 (T1) vs. 2026-09-05 (T2)',
        area: 'Gudlavalleru, Krishna District, AP, India',
        resolution: '10 m GSD',
        source: 'Sentinel-2 L2A Archive (10m L2A)',
        image: '/static/thumbs/gvl_s2_2026_09_05.jpg',
        split_image: '/static/thumbs/gvl_s2_2025_09_03.jpg',
        query: 'What changed between 2025 and 2026 in this area?',
        scene_ids: 'gvl_s2_2025_09_03,gvl_s2_2026_09_05',
        analysis_mode: 'change'
      },
      'avanigadda': {
        name: 'Avanigadda, Krishna River Delta, AP',
        coords: '16.0193°N, 80.9151°E',
        bbox: 'BBox: [15.98, 80.88, 16.06, 80.96]',
        feature: 'Krishna Delta Estuary, Mangroves, Aquaculture & River Islands',
        date: '2025-08-20 (T1) vs. 2026-09-02 (T2)',
        area: 'Avanigadda, Krishna River Delta, AP, India',
        resolution: '10 m GSD',
        source: 'Copernicus Sentinel-2 Delta Archive',
        image: '/static/thumbs/avanigadda_s2_2026.jpg',
        split_image: '/static/thumbs/avanigadda_s2_2025.jpg',
        query: 'What environmental and aquaculture changes occurred in Avanigadda between 2025 and 2026?',
        scene_ids: 'avanigadda_s2_2025,avanigadda_s2_2026',
        analysis_mode: 'change'
      },
      'vijayawada': {
        name: 'Vijayawada, Krishna District, AP',
        coords: '16.5100°N, 80.6500°E',
        bbox: 'BBox: [16.45, 80.58, 16.57, 80.71]',
        feature: 'Krishna River Basin, Prakasam Barrage, Urban Core',
        date: '2025-08-15 (T1) vs. 2026-09-02 (T2)',
        area: 'Vijayawada, Krishna District, AP, India',
        resolution: '10 m GSD',
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
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/tpt_s2_2026_09_03.jpg',
        split_image: '/static/thumbs/tpt_s2_2025_08_11.jpg',
        query: 'Identify built-up growth and transit infrastructure changes near foothills.',
        scene_ids: 'tpt_s2_2025_08_11,tpt_s2_2026_09_03',
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
        source: 'Sentinel-2 L2A State-Wide AP Archive',
        image: '/static/thumbs/knl_s2_2026_09_04.jpg',
        split_image: '/static/thumbs/knl_s2_2025_08_10.jpg',
        query: 'Detect newly installed solar photovoltaic panels and arid land transformation.',
        scene_ids: 'knl_s2_2025_08_10,knl_s2_2026_09_04',
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
        source: 'State-Wide Sentinel-2 Regional Composite',
        image: '/static/thumbs/ap_s2_2026_09_03.jpg',
        split_image: '/static/thumbs/ap_s2_2025_08_22.jpg',
        query: 'Analyze state-wide regional hydrological condition and vegetation change.',
        scene_ids: 'ap_s2_2025_08_22,ap_s2_2026_09_03',
        analysis_mode: 'change'
      }
    };

    window.onload = () => {
      selectApCity('gudlavalleru');
    };

    function switchModeTab(tabKey) {
      ['demo', 'copernicus', 'upload'].forEach(t => {
        const btn = document.getElementById('tabBtn' + t.charAt(0).toUpperCase() + t.slice(1));
        const content = document.getElementById('tabContent' + t.charAt(0).toUpperCase() + t.slice(1));
        if (t === tabKey) {
          btn.className = 'flex-1 py-2 px-2.5 rounded-lg text-xs font-semibold bg-crimson-600 text-white transition flex items-center justify-center space-x-1.5 shadow';
          content.classList.remove('hidden');
        } else {
          btn.className = 'flex-1 py-2 px-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center justify-center space-x-1.5';
          content.classList.add('hidden');
        }
      });
      if (tabKey === 'copernicus') {
        executeCopernicusSearch();
      }
    }

    function selectApCity(cityKey) {
      const loc = AP_SCENARIOS_CATALOG[cityKey];
      if (!loc) return;
      const inp = document.getElementById('dashboardLocSearch');
      if (inp) inp.value = loc.name.split(',')[0].trim();
      applyLocation(loc);
    }

    async function searchLocationDashboard() {
      const rawQ = (document.getElementById('dashboardLocSearch')?.value || '').trim();
      const q = rawQ.toLowerCase();
      if (!q) {
        selectApCity('gudlavalleru');
        return;
      }
      for (const [k, loc] of Object.entries(AP_SCENARIOS_CATALOG)) {
        if (q.includes(k) || k.includes(q) || loc.name.toLowerCase().includes(q)) {
          applyLocation(loc);
          return;
        }
      }
      // If not in preloaded catalog, seamlessly query live Copernicus API!
      switchModeTab('copernicus');
      document.getElementById('copernicusPlaceInput').value = rawQ;
      executeCopernicusSearch();
    }

    function updateCoordinatesHUD(locationName, coordsStr, bboxStr) {
      const hudLoc = document.getElementById('hudLocationName');
      const hudCoords = document.getElementById('hudLatLon');
      const hudB = document.getElementById('hudBbox');
      const badge = document.getElementById('sceneCoordinatesBadge');

      if (hudLoc) hudLoc.innerText = (locationName || 'TARGET AOI').toUpperCase();
      if (hudCoords) hudCoords.innerText = coordsStr || '16.0200° N, 80.7000° E';
      if (hudB) hudB.innerText = bboxStr || '[15.98, 80.65, 16.08, 80.75]';
      if (badge) badge.innerText = 'LAT/LON: ' + (coordsStr || '16.0200° N, 80.7000° E');
    }

    function applyLocation(loc) {
      activeScenarioId = null;
      selectedFiles = [];
      activeSceneIds = loc.scene_ids;
      activeAnalysisMode = loc.analysis_mode;

      const coordEl = document.getElementById('dashboardAoiCoords');
      if (coordEl) coordEl.innerText = `AOI: ${loc.coords} (${loc.name.split(',')[0]})`;
      updateCoordinatesHUD(loc.name.split(',')[0], loc.coords, loc.bbox);

      setQuery(loc.query);
      document.getElementById('viewerBaseImg').src = loc.image;
      if (loc.split_image) {
        document.getElementById('viewerSplitImg').src = loc.split_image;
      }
      document.getElementById('sceneDataSource').innerText = `Sentinel-2 L2A, ${loc.date}, ${loc.area}`;
      document.getElementById('sceneResolution').innerText = loc.resolution;
      document.getElementById('traceDataSource').innerText = `Copernicus Archive (${loc.source})`;

      document.querySelectorAll('.scenario-btn').forEach(b => {
        b.className = 'scenario-btn w-full text-left p-2.5 rounded-lg border border-void-800 bg-void-950 hover:border-crimson-500 transition';
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

      activeSceneIds = meta.scene_ids || null;
      activeAnalysisMode = meta.analysis_mode || null;

      updateCoordinatesHUD(meta.name, meta.coords || '16.0200°N, 80.7000°E', meta.bbox || '[15.98, 80.65, 16.08, 80.75]');

      setQuery(meta.query);
      document.getElementById('viewerBaseImg').src = meta.image;
      if (meta.split_image) {
        document.getElementById('viewerSplitImg').src = meta.split_image;
      }
      document.getElementById('sceneDataSource').innerText = `${meta.sensor}, ${meta.date}, ${meta.area}`;
      document.getElementById('sceneResolution').innerText = meta.resolution;
      document.getElementById('traceDataSource').innerText = `${scenarioId} (${meta.source})`;

      document.querySelectorAll('.scenario-btn').forEach(b => {
        b.className = 'scenario-btn w-full text-left p-2.5 rounded-lg border border-void-800 bg-void-950 hover:border-crimson-500 transition';
      });
      const btn = document.getElementById('btn_' + scenarioId);
      if (btn) {
        btn.className = 'scenario-btn w-full text-left p-2.5 rounded-lg border border-crimson-600 bg-void-850 hover:border-crimson-400 transition';
      }

      resetViewerOverlays();
    }

    async function executeCopernicusSearch() {
      const place = document.getElementById('copernicusPlaceInput').value.trim() || 'Vijayawada';
      const maxCloud = document.getElementById('cloudCoverSlider').value || 20;
      const resultsContainer = document.getElementById('copernicusResultsList');
      resultsContainer.innerHTML = '<div class="text-center py-6 text-xs text-crimson-400 font-medium animate-pulse"><i class="fa-solid fa-circle-notch fa-spin mr-2"></i>Querying Copernicus Data Space Ecosystem...</div>';

      try {
        const res = await fetch(`/api/copernicus/scenes?aoi_name=${encodeURIComponent(place)}&max_cloud=${maxCloud}`);
        if (!res.ok) throw new Error('Copernicus query failed');
        const data = await res.json();
        renderCopernicusScenes(data);

        // Auto-load discovered satellite scene immediately into viewport
        if (data.scenes && data.scenes.length > 0) {
          const latLon = data.coordinates_display || `${data.latitude ? data.latitude.toFixed(4) + '° N' : ''}, ${data.longitude ? data.longitude.toFixed(4) + '° E' : ''}`;
          const bboxStr = data.bbox_display || (data.bbox ? `[${data.bbox.join(', ')}]` : '');
          if (data.scenes.length >= 2) {
            const s1 = data.scenes[0];
            const s2 = data.scenes[1];
            loadCopernicusPair(s1.id, s2.id, s2.thumbnail_url || '', s1.thumbnail_url || '', data.aoi, s1.date, s2.date, latLon, bboxStr);
          } else {
            const s0 = data.scenes[0];
            loadCopernicusScene(s0.id, s0.thumbnail_url || '', data.aoi, s0.date, latLon, bboxStr);
          }
        }
      } catch (err) {
        resultsContainer.innerHTML = `<div class="p-3 text-xs text-crimson-300 bg-crimson-950/40 border border-crimson-800 rounded-lg">Unable to reach Copernicus CDSE endpoint: ${err.message}. Displaying local cached scenes.</div>`;
      }
    }

    function renderCopernicusScenes(data) {
      const container = document.getElementById('copernicusResultsList');
      container.innerHTML = '';
      if (!data.scenes || data.scenes.length === 0) {
        container.innerHTML = '<div class="p-3 text-xs text-slate-400">No scenes found matching cloud cover threshold. Try increasing slider limit.</div>';
        return;
      }

      const latLon = data.coordinates_display || `${data.latitude ? data.latitude.toFixed(4) + '° N' : ''}, ${data.longitude ? data.longitude.toFixed(4) + '° E' : ''}`;
      const bboxStr = data.bbox_display || (data.bbox ? `[${data.bbox.join(', ')}]` : '');
      const safeAoi = (data.aoi || 'Target Area').replace(/'/g, "\\'");

      const headerDiv = document.createElement('div');
      headerDiv.className = 'text-[11px] text-slate-400 mb-1 flex items-center justify-between';
      headerDiv.innerHTML = `<span>Found <b>${data.scenes.length}</b> Sentinel-2 scenes for <i>${data.aoi}</i>:</span><span class="text-[9px] text-emerald-400 font-mono font-bold">${latLon}</span>`;
      container.appendChild(headerDiv);

      // Bi-Temporal Comparison Card if at least 2 scenes
      if (data.scenes.length >= 2) {
        const s1 = data.scenes[0];
        const s2 = data.scenes[1];
        const compareDiv = document.createElement('div');
        compareDiv.className = 'p-2.5 rounded-lg bg-crimson-950/80 border border-crimson-700/90 mb-2 space-y-1.5 shadow';
        compareDiv.innerHTML = `
          <div class="flex items-center justify-between text-[11px] text-slate-200">
            <span class="font-semibold text-crimson-300 flex items-center space-x-1">
              <i class="fa-solid fa-code-compare"></i>
              <span>Bi-Temporal Pair Available</span>
            </span>
            <span class="text-[9px] font-mono bg-crimson-900 px-1.5 py-0.5 rounded text-white">${s1.date} vs ${s2.date}</span>
          </div>
          <button onclick="loadCopernicusPair('${s1.id}', '${s2.id}', '${s2.thumbnail_url || ''}', '${s1.thumbnail_url || ''}', '${safeAoi}', '${s1.date}', '${s2.date}', '${latLon}', '${bboxStr}')" class="w-full bg-crimson-600 hover:bg-crimson-500 text-white font-semibold text-xs py-1.5 px-3 rounded shadow transition flex items-center justify-center space-x-1.5">
            <i class="fa-solid fa-layer-group text-[10px]"></i>
            <span>Load Both Scenes for Change Detection</span>
          </button>
        `;
        container.appendChild(compareDiv);
      }

      data.scenes.forEach((sc, idx) => {
        const item = document.createElement('div');
        item.className = 'p-2 rounded-lg bg-void-950 border border-void-800 hover:border-crimson-700/80 transition flex items-center justify-between text-xs gap-2';
        const scLatLon = sc.coordinates_display || latLon;
        const scBbox = sc.bbox_display || bboxStr;
        item.innerHTML = `
          <div class="flex items-center space-x-2.5 overflow-hidden">
            <img src="${sc.thumbnail_url || '/static/thumbs/vja_s2_2026_09_02.jpg'}" onerror="this.src='/static/thumbs/gvl_s2_2026_09_05.jpg'" class="w-10 h-10 rounded object-cover border border-void-700 flex-shrink-0">
            <div class="overflow-hidden">
              <div class="font-semibold text-slate-200 text-[11px] truncate">${sc.id.split('_').slice(0,3).join('_')}</div>
              <div class="text-[10px] text-slate-400 flex items-center space-x-2">
                <span>Date: <b class="text-white">${sc.date}</b></span>
                <span>&bull;</span>
                <span class="text-emerald-400 font-mono text-[9px]">${scLatLon}</span>
                <span>&bull;</span>
                <span>Cloud: <b class="${sc.cloud_cover <= 10 ? 'text-emerald-400' : 'text-amber-400'}">${sc.cloud_cover}%</b></span>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-1 flex-shrink-0">
            <button onclick="loadCopernicusScene('${sc.id}', '${sc.thumbnail_url || ''}', '${safeAoi}', '${sc.date}', '${scLatLon}', '${scBbox}')" class="bg-crimson-600 hover:bg-crimson-500 text-white text-[10px] font-semibold px-2.5 py-1 rounded transition shadow flex items-center space-x-1">
              <i class="fa-solid fa-satellite text-[9px]"></i>
              <span>Load Scene</span>
            </button>
          </div>
        `;
        container.appendChild(item);
      });
    }

    function loadCopernicusScene(sceneId, thumbUrl, aoi, date, latLon, bboxStr) {
      activeScenarioId = null;
      activeSceneIds = sceneId;
      activeAnalysisMode = 'single';
      selectedFiles = [];

      const targetThumb = thumbUrl || '/static/thumbs/vja_s2_2026_09_02.jpg';
      document.getElementById('viewerBaseImg').src = targetThumb;
      document.getElementById('sceneDataSource').innerText = `Copernicus Sentinel-2 (${date}), ${aoi}`;
      document.getElementById('sceneResolution').innerText = '10 m GSD';
      updateCoordinatesHUD(aoi, latLon || '16.0200° N, 80.7000° E', bboxStr || 'Copernicus Sentinel-2 BBox');

      setQuery(`Analyze surface features, land use, and infrastructure in ${aoi}.`);
      resetViewerOverlays();

      const toast = document.getElementById('toastNotice');
      if (toast) {
        toast.innerHTML = `<span class="flex items-center space-x-1.5"><i class="fa-solid fa-circle-check text-emerald-400"></i><span>Loaded Sentinel-2 scene for <b>${aoi}</b> [${latLon || ''}]. Click <b>Analyze Satellite Images</b> below!</span></span>`;
        toast.classList.remove('hidden');
      }
    }

    function loadCopernicusPair(sid1, sid2, thumb2, thumb1, aoi, date1, date2, latLon, bboxStr) {
      activeScenarioId = null;
      activeSceneIds = `${sid1},${sid2}`;
      activeAnalysisMode = 'change';
      selectedFiles = [];

      document.getElementById('viewerBaseImg').src = thumb2 || '/static/thumbs/vja_s2_2026_09_02.jpg';
      if (thumb1) {
        document.getElementById('viewerSplitImg').src = thumb1;
      }
      document.getElementById('sceneDataSource').innerText = `Copernicus Sentinel-2 (${date1} vs ${date2}), ${aoi}`;
      document.getElementById('sceneResolution').innerText = '10 m GSD';
      updateCoordinatesHUD(aoi, latLon || '16.0200° N, 80.7000° E', bboxStr || 'Copernicus Sentinel-2 BBox');

      setQuery(`What infrastructure and environmental changes occurred in ${aoi} between ${date1} and ${date2}?`);
      resetViewerOverlays();

      const toast = document.getElementById('toastNotice');
      if (toast) {
        toast.innerHTML = `<span class="flex items-center space-x-1.5"><i class="fa-solid fa-code-compare text-crimson-400"></i><span>Loaded bi-temporal Sentinel-2 pair for <b>${aoi}</b> [${latLon || ''}]. Click <b>Analyze Satellite Images</b> below!</span></span>`;
        toast.classList.remove('hidden');
      }
    }

    function handleFileSelect(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        selectedFiles = Array.from(files);
        activeScenarioId = null;
        activeSceneIds = null;
        activeAnalysisMode = null;
        document.getElementById('uploadLabel').innerText = `${files.length} custom file(s) loaded: ` + Array.from(files).map(f => f.name).join(', ');
        document.getElementById('sceneDataSource').innerText = `Custom Upload (${files[0].name})`;

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

    async function executeAnalysis(customQuery) {
      const query = (customQuery || document.getElementById('queryInput').value).trim();
      if (!query) {
        alert('Please enter a natural language query.');
        return;
      }

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
      } else if (currentSessionTraceId) {
        formData.append('session_trace_id', currentSessionTraceId);
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
        currentSessionTraceId = currentResponse.execution_trace.trace_id;
        renderAnalysisResults(currentResponse, query);
      } catch (error) {
        alert('Error during execution: ' + error.message);
      } finally {
        document.getElementById('loadingOverlay').classList.add('hidden');
        document.getElementById('executeBtn').disabled = false;
      }
    }

    async function executeFollowUpQuery() {
      const q = document.getElementById('followUpQueryInput').value.trim();
      if (!q) return;
      document.getElementById('followUpQueryInput').value = '';
      await executeAnalysis(q);
    }

    function renderAnalysisResults(data, queryUsed) {
      // 1. Task badge
      const badge = document.getElementById('detectedBadge');
      badge.classList.remove('hidden');
      badge.innerText = 'Task: ' + data.detected_task.toUpperCase().replace('_', ' ');

      // 2. Answer text
      document.getElementById('answerText').innerText = data.result.text_answer;

      // 3. Confidence score & calibration explanation
      const confPct = Math.round(data.result.confidence_score * 100);
      document.getElementById('confidenceBar').style.width = confPct + '%';
      document.getElementById('confidenceValue').innerText = confPct + '%';

      if (data.result.confidence_explanation) {
        const reasonBox = document.getElementById('confidenceReasonBox');
        reasonBox.classList.remove('hidden');
        document.getElementById('confidenceReasonText').innerText = data.result.confidence_explanation;
      }

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

        document.getElementById('mapLegend').classList.remove('hidden');
        setViewMode('overlay');
      }

      // 6. Trace Telemetry
      document.getElementById('traceIdBadge').innerText = 'ID: ' + data.execution_trace.trace_id;
      document.getElementById('traceRouterReasoning').innerText = data.execution_trace.router_reasoning;
      document.getElementById('traceLatency').innerText = data.execution_trace.total_execution_time_ms + ' ms';
      if (data.execution_trace.data_source_label) {
        document.getElementById('traceDataSource').innerText = data.execution_trace.data_source_label;
      }

      const toolsList = document.getElementById('traceToolsList');
      toolsList.innerHTML = '';
      data.execution_trace.tools_executed.forEach(t => {
        const div = document.createElement('div');
        div.className = 'p-2 rounded bg-void-950 border border-void-800 flex justify-between items-center text-[11px]';
        div.innerHTML = `
          <div>
            <b class="text-crimson-400">${t.tool_name}</b>
            <span class="text-slate-500 block text-[9px] font-mono">${t.model_checkpoint}</span>
          </div>
          <div class="text-right font-mono">
            <span class="text-emerald-400">${t.execution_time_ms} ms</span>
            <span class="text-slate-500 block text-[9px]">Conf: ${(t.confidence*100).toFixed(1)}%</span>
          </div>
        `;
        toolsList.appendChild(div);
      });

      // 7. Multi-Query Session History Thread
      const chatBox = document.getElementById('chatHistoryBox');
      const chatItem = document.createElement('div');
      chatItem.className = 'p-2 rounded bg-void-950 border border-void-800 text-[11px] space-y-1';
      chatItem.innerHTML = `
        <div class="text-crimson-400 font-medium"><i class="fa-solid fa-circle-question mr-1"></i>${queryUsed || data.query}</div>
        <div class="text-slate-300 text-[10px] pl-3 border-l border-crimson-900/60 leading-relaxed">${data.result.text_answer.slice(0, 160)}...</div>
      `;
      chatBox.appendChild(chatItem);
      chatBox.scrollTop = chatBox.scrollHeight;
      document.getElementById('sessionActiveBadge').classList.remove('hidden');

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
        btnBase.className = 'px-2.5 py-1 rounded bg-crimson-600 text-white font-medium text-[11px] transition';
        overlayImg.classList.add('hidden');
        splitCont.classList.add('hidden');
      } else if (mode === 'overlay') {
        btnOverlay.className = 'px-2.5 py-1 rounded bg-crimson-600 text-white font-medium text-[11px] transition';
        overlayImg.classList.remove('hidden');
        splitCont.classList.add('hidden');
      } else if (mode === 'split') {
        btnSplit.className = 'px-2.5 py-1 rounded bg-red-700 text-white font-medium text-[11px] transition';
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

    function openTraceModal() {
      const m = document.getElementById('traceModal');
      if (!m) return;
      if (currentResponse && currentResponse.execution_trace) {
        document.getElementById('modalTraceId').innerText = 'Trace ID: ' + currentResponse.execution_trace.trace_id;
        document.getElementById('traceJsonViewer').innerText = JSON.stringify(currentResponse, null, 2);
      } else {
        document.getElementById('modalTraceId').innerText = 'Trace ID: Demo Preset Baseline';
        document.getElementById('traceJsonViewer').innerText = JSON.stringify({
          status: "ready",
          system: "SatQuery AI",
          ps_id: "26167",
          theme: "Space Technology",
          copernicus_status: "connected",
          agentic_router: "active",
          registry_tools: ["vqa_tool", "grounding_tool", "change_tool", "fusion_tool"]
        }, null, 2);
      }
      m.classList.remove('hidden');
    }

    function closeTraceModal() {
      const m = document.getElementById('traceModal');
      if (m) m.classList.add('hidden');
    }

    function copyTraceJson() {
      const txt = document.getElementById('traceJsonViewer').innerText;
      navigator.clipboard.writeText(txt);
      alert('Audit trace JSON copied to clipboard!');
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeDataModal();
        closeTraceModal();
      }
    });
    document.addEventListener('click', (e) => {
      if (e.target === document.getElementById('dataGuideModal')) closeDataModal();
      if (e.target === document.getElementById('traceModal')) closeTraceModal();
    });
  </script>
</body>
</html>
"""
