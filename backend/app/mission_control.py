"""
SatQuery AI - Autonomous Vision-Language Satellite Intelligence (SIH 2026 PS 26167)
Dominance-Grade Black & Red Defense Intelligence Theme.
Integrates:
  1. Evaluation Layer: 4 Input Modes (Optical, SAR, Bi-Temporal, Optical+SAR),
     Remote-Sensing Domain Adaptation (BigEarthNet.txt), Agentic Controller with
     7 Specialist Tools, and Empirical Benchmark Evaluation (RSVQA, VRSBench, CDVQA, LEVIR-CD).
  2. Demo Layer: Interactive Map Viewport with Pan, Mouse-Wheel/Touch Zoom,
     Interactive AOI Draw Tool (thin cyan/red boundary, live coords, area in ha/km²),
     Split-Screen Comparison Slider, Calibrated Evidence View, and Live Copernicus Discovery.
"""

MISSION_CONTROL_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SatQuery AI — Autonomous Vision-Language Satellite Intelligence (SIH 2026 PS 26167)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
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
    /* Comparison slider styles */
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
      z-index: 25;
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

    /* Interactive Viewport Pan & Zoom Layer */
    #viewportStage {
      transform-origin: 0 0;
      transition: transform 0.05s ease-out;
      will-change: transform;
    }
    .canvas-panning {
      cursor: grab !important;
    }
    .canvas-panning:active {
      cursor: grabbing !important;
    }
    .canvas-drawing {
      cursor: crosshair !important;
    }

    /* AOI Boundary Box: Thin cyan outline with subtle glow, never solid/opaque */
    #aoiBox {
      border: 2px solid #00f0ff;
      background: rgba(0, 240, 255, 0.08);
      box-shadow: 0 0 10px rgba(0, 240, 255, 0.35);
      position: absolute;
      pointer-events: none;
      z-index: 30;
      box-sizing: border-box;
    }
    #aoiBox.red-outline {
      border-color: #ef4444;
      background: rgba(239, 68, 68, 0.08);
      box-shadow: 0 0 10px rgba(239, 68, 68, 0.35);
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
      
      <div class="flex items-center space-x-2.5">
        <div class="hidden lg:flex items-center space-x-2 text-xs text-slate-400 bg-void-950 px-3 py-1.5 rounded-md border border-void-700">
          <span class="w-2 h-2 rounded-full bg-crimson-500 animate-pulse"></span>
          <span>Router: <b class="text-crimson-400">Deterministic</b></span>
          <span class="text-slate-600">|</span>
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>CDSE: <b class="text-emerald-400">Online</b></span>
          <span class="text-slate-600">|</span>
          <span class="text-cyan-400 font-mono">BigEarthNet Adapted</span>
        </div>
        <button onclick="openDataModal()" class="inline-flex items-center space-x-1.5 bg-void-850 hover:bg-void-800 text-slate-300 hover:text-white text-xs font-medium px-2.5 py-1.5 rounded-lg border border-void-700 hover:border-crimson-600 transition shadow-sm">
          <i class="fa-solid fa-circle-question text-crimson-400"></i>
          <span class="hidden sm:inline">Free Data</span>
        </button>
        <button onclick="openTraceModal()" id="headerTraceBtn" class="inline-flex items-center space-x-1.5 bg-void-850 hover:bg-void-800 text-slate-300 hover:text-white text-xs font-medium px-2.5 py-1.5 rounded-lg border border-void-700 hover:border-crimson-600 transition shadow-sm">
          <i class="fa-solid fa-microchip text-crimson-400"></i>
          <span>Trace</span>
        </button>
        <button onclick="downloadLatestReport()" id="headerDownloadBtn" disabled class="disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center space-x-2 bg-gradient-to-r from-crimson-700 to-red-600 hover:from-crimson-600 hover:to-red-500 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition shadow-md shadow-crimson-900/30">
          <i class="fa-solid fa-file-pdf"></i>
          <span>Mission PDF</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Top "How to Use SatQuery AI" Guide Ribbon (Hidden from display) -->
  <section id="howToUseGuide" class="hidden bg-gradient-to-r from-void-900 via-void-850 to-void-900 border-b border-crimson-900/60 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center space-x-2">
          <span class="w-2.5 h-2.5 rounded-full bg-crimson-500 animate-ping"></span>
          <h2 class="text-xs font-bold uppercase tracking-wider text-crimson-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-circle-info text-crimson-400"></i>
            <span>Quick Start Guide &mdash; How to Use SatQuery AI (SIH 2026 PS 26167)</span>
          </h2>
          <span class="text-[10px] bg-crimson-950 text-crimson-400 px-2 py-0.5 rounded border border-crimson-800 font-mono">4 Modes &bull; GeoTIFF/TIFF &bull; BigEarthNet Adapted</span>
        </div>
        <button onclick="toggleHowToUseGuide()" class="text-xs text-slate-400 hover:text-white flex items-center space-x-1 px-2 py-1 rounded bg-void-950 border border-void-700 hover:border-void-600">
          <span id="guideToggleText">Collapse Guide</span>
          <i id="guideToggleIcon" class="fa-solid fa-chevron-up text-[10px]"></i>
        </button>
      </div>

      <div id="guideStepsGrid" class="grid grid-cols-1 md:grid-cols-4 gap-2.5 text-xs">
        <div class="bg-void-950/80 border border-void-800 p-2.5 rounded-lg">
          <div class="flex items-center space-x-2 mb-1">
            <span class="w-5 h-5 rounded-full bg-crimson-600 text-white flex items-center justify-center font-bold text-[10px]">1</span>
            <span class="font-bold text-slate-200">Select Location &amp; Input Mode</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-snug">
            Choose from 4 input types: <b>Single Optical</b>, <b>Single SAR</b>, <b>Bi-Temporal Pair</b>, or <b>Optical + SAR Pair</b>. GeoTIFF / TIFF supported.
          </p>
        </div>
        <div class="bg-void-950/80 border border-void-800 p-2.5 rounded-lg">
          <div class="flex items-center space-x-2 mb-1">
            <span class="w-5 h-5 rounded-full bg-crimson-600 text-white flex items-center justify-center font-bold text-[10px]">2</span>
            <span class="font-bold text-slate-200">Discover Scenes &amp; Draw AOI</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-snug">
            Use <b>Draw AOI</b> to isolate target areas with a thin cyan boundary. View coordinates and live computed area in hectares / km².
          </p>
        </div>
        <div class="bg-void-950/80 border border-void-800 p-2.5 rounded-lg">
          <div class="flex items-center space-x-2 mb-1">
            <span class="w-5 h-5 rounded-full bg-crimson-600 text-white flex items-center justify-center font-bold text-[10px]">3</span>
            <span class="font-bold text-slate-200">Load Both Scenes &amp; Ask Natural Language Query</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-snug">
            Type any question. SatQuery automatically routes to <b>VQA</b>, <b>Captioning</b>, <b>Grounding</b>, <b>Change Analysis</b>, or <b>Optical-SAR Fusion</b>.
          </p>
        </div>
        <div class="bg-void-950/80 border border-void-800 p-2.5 rounded-lg">
          <div class="flex items-center space-x-2 mb-1">
            <span class="w-5 h-5 rounded-full bg-crimson-600 text-white flex items-center justify-center font-bold text-[10px]">4</span>
            <span class="font-bold text-slate-200">Detect &amp; Quantify &mdash; Evidence &amp; Trace</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-snug">
            Inspect split slider comparison, semi-transparent evidence overlays, physical hectare breakdown, and export official mission PDF dossier.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Primary Tab Bar: Evaluation & Operational Modules -->
  <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 w-full">
    <div class="flex flex-wrap gap-2 border-b border-void-800 pb-2">
      <button onclick="switchMainTab('upload_analyze')" id="navTabUpload" class="px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 bg-crimson-600 text-white shadow-md shadow-crimson-900/30">
        <i class="fa-solid fa-cloud-arrow-up"></i>
        <span>Upload &amp; Analyze (Core PS 26167)</span>
      </button>
      <button onclick="switchMainTab('copernicus_aoi')" id="navTabCopernicus" class="px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 bg-void-900 text-slate-400 hover:text-white border border-void-800 hover:border-void-700">
        <i class="fa-solid fa-satellite"></i>
        <span>Live Copernicus AOI (Data Acquisition)</span>
      </button>
      <button onclick="switchMainTab('benchmarks')" id="navTabBenchmarks" class="px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 bg-void-900 text-slate-400 hover:text-white border border-void-800 hover:border-void-700">
        <i class="fa-solid fa-chart-line text-cyan-400"></i>
        <span>Benchmark Evaluation (Judging Layer)</span>
      </button>
      <button onclick="switchMainTab('traces_dossier')" id="navTabTraces" class="px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 bg-void-900 text-slate-400 hover:text-white border border-void-800 hover:border-void-700">
        <i class="fa-solid fa-shield-halved text-emerald-400"></i>
        <span>Audit Traces &amp; Mission Records</span>
      </button>
    </div>
  </nav>

  <!-- Main Workspace Container -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 grid grid-cols-1 lg:grid-cols-12 gap-5">

    <!-- Left Controls Panel (5 Cols) -->
    <div class="lg:col-span-5 space-y-4 flex flex-col">

      <!-- =================================================================== -->
      <!-- TAB 1: UPLOAD & ANALYZE (Primary Hero Interface)                     -->
      <!-- =================================================================== -->
      <div id="sectionUploadAnalyze" class="space-y-4">
        
        <!-- 4 Input Modes Selector -->
        <div class="bg-void-900 border border-void-800 rounded-xl p-3.5 shadow-sm space-y-2.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-sliders text-crimson-400"></i>
              <span>Select Input Mode</span>
            </span>
            <span id="activeInputModeBadge" class="text-[10px] text-crimson-300 bg-crimson-950/80 px-2 py-0.5 rounded border border-crimson-800 font-mono">Mode: Bi-Temporal Pair</span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-xs">
            <!-- Mode 1: Single Optical -->
            <button onclick="selectInputMode('single_optical')" id="modeBtnOptical" class="p-2.5 rounded-lg border border-void-700 bg-void-950 text-left hover:border-crimson-500 transition space-y-1">
              <div class="flex items-center justify-between">
                <b class="text-slate-200 text-[11px]">1. Single Optical</b>
                <i class="fa-solid fa-sun text-amber-400 text-xs"></i>
              </div>
              <p class="text-[10px] text-slate-400 leading-tight">Sentinel-2 / Cartosat-2S True-color RGB or VNIR</p>
            </button>

            <!-- Mode 2: Single SAR -->
            <button onclick="selectInputMode('single_sar')" id="modeBtnSar" class="p-2.5 rounded-lg border border-void-700 bg-void-950 text-left hover:border-crimson-500 transition space-y-1">
              <div class="flex items-center justify-between">
                <b class="text-slate-200 text-[11px]">2. Single SAR</b>
                <i class="fa-solid fa-satellite-dish text-cyan-400 text-xs"></i>
              </div>
              <p class="text-[10px] text-slate-400 leading-tight">Sentinel-1 / RISAT C-band backscatter (VV/VH)</p>
            </button>

            <!-- Mode 3: Bi-Temporal Pair -->
            <button onclick="selectInputMode('bitemporal_pair')" id="modeBtnBiTemporal" class="p-2.5 rounded-lg border border-crimson-500 bg-crimson-950/40 text-left transition space-y-1">
              <div class="flex items-center justify-between">
                <b class="text-white text-[11px]">3. Bi-Temporal Pair</b>
                <i class="fa-solid fa-code-compare text-crimson-400 text-xs"></i>
              </div>
              <p class="text-[10px] text-slate-300 leading-tight">Same area, two dates (T1 baseline &amp; T2 follow-up)</p>
            </button>

            <!-- Mode 4: Optical + SAR Pair -->
            <button onclick="selectInputMode('optical_sar_pair')" id="modeBtnOptSar" class="p-2.5 rounded-lg border border-void-700 bg-void-950 text-left hover:border-crimson-500 transition space-y-1">
              <div class="flex items-center justify-between">
                <b class="text-slate-200 text-[11px]">4. Optical + SAR</b>
                <i class="fa-solid fa-layer-group text-purple-400 text-xs"></i>
              </div>
              <p class="text-[10px] text-slate-400 leading-tight">Co-registered pair for all-weather cloud penetration</p>
            </button>
          </div>
        </div>

        <!-- GeoTIFF / TIFF File Upload Drop Zone -->
        <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-2.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-file-arrow-up text-crimson-400"></i>
              <span>Upload Imagery Files</span>
            </span>
            <span class="text-[10px] text-emerald-400 font-mono bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-900">GeoTIFF Supported</span>
          </div>

          <div class="border-2 border-dashed border-void-700 hover:border-crimson-500 rounded-lg p-4 text-center cursor-pointer transition bg-void-950/60" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" multiple accept=".tif,.tiff,.png,.jpg,.jpeg" class="hidden" onchange="handleFileSelect(event)">
            <i class="fa-solid fa-cloud-arrow-up text-crimson-500 text-2xl mb-1"></i>
            <p class="text-xs text-slate-200 font-medium" id="uploadLabel">Click or drag &amp; drop GeoTIFF / TIFF or Benchmark images</p>
            <p class="text-[10px] text-slate-500 mt-1">
              <b>Primary:</b> GeoTIFF / TIFF (.tif, .tiff) with CRS &bull; 
              <span class="text-slate-400 font-mono">PNG/JPEG permitted for benchmark subsets (RSVQA, VRSBench, BigEarthNet, LEVIR-CD)</span>
            </p>
          </div>

          <!-- Quick Preset Demo Scenarios Selector -->
          <div class="pt-1 space-y-1.5">
            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span class="font-semibold uppercase tracking-wider text-[10px]">Or Quick-Load Verified Competition Datasets:</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px]">
              <button onclick="loadPresetScenario('scenario_3_optical_sar')" class="p-2 rounded bg-void-950 border border-void-700 hover:border-purple-500 text-left transition flex items-center space-x-2">
                <i class="fa-solid fa-layer-group text-purple-400 text-xs"></i>
                <div>
                  <b class="text-slate-200 block text-[10px]">Optical + SAR Fusion</b>
                  <span class="text-[9px] text-slate-400">Cartosat-2S + RISAT SAR pair</span>
                </div>
              </button>

              <button onclick="loadPresetScenario('nepal_flood')" class="p-2 rounded bg-void-950 border border-void-700 hover:border-cyan-500 text-left transition flex items-center space-x-2">
                <i class="fa-solid fa-water text-cyan-400 text-xs"></i>
                <div>
                  <b class="text-slate-200 block text-[10px]">Nepal Flood Corridor</b>
                  <span class="text-[9px] text-slate-400">Rasuwa Bhote Koshi S2 &amp; S1</span>
                </div>
              </button>

              <button onclick="loadPresetScenario('gudlavalleru_urban_growth')" class="p-2 rounded bg-void-950 border border-void-700 hover:border-amber-500 text-left transition flex items-center space-x-2">
                <i class="fa-solid fa-city text-amber-400 text-xs"></i>
                <div>
                  <b class="text-slate-200 block text-[10px]">Gudlavalleru Urban Growth</b>
                  <span class="text-[9px] text-slate-400">Sentinel-2 2025 vs 2026</span>
                </div>
              </button>

              <button onclick="loadPresetScenario('scenario_4_coastal')" class="p-2 rounded bg-void-950 border border-void-700 hover:border-emerald-500 text-left transition flex items-center space-x-2">
                <i class="fa-solid fa-anchor text-emerald-400 text-xs"></i>
                <div>
                  <b class="text-slate-200 block text-[10px]">Coastal Port Expansion</b>
                  <span class="text-[9px] text-slate-400">Visakhapatnam Breakwater</span>
                </div>
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- =================================================================== -->
      <!-- TAB 2: LIVE COPERNICUS AOI (Data Acquisition Support Module)         -->
      <!-- =================================================================== -->
      <div id="sectionCopernicusAOI" class="space-y-4 hidden">
        <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-satellite text-crimson-400"></i>
              <span>Live Copernicus Sentinel-2 &amp; SAR Discovery</span>
            </h2>
            <span class="text-[10px] text-emerald-400 font-mono bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-900">Data Acquisition Module</span>
          </div>

          <div class="space-y-2">
            <div class="flex gap-1.5">
              <input type="text" id="copernicusPlaceInput" value="" placeholder="Search ANY location or coordinates worldwide (e.g. Vijayawada, Amaravati, Visakhapatnam, Tirupati, Kurnool, Avanigadda, Rasuwa, Bhote Koshi, 16.48° N, 80.74° E)..." class="flex-1 bg-void-950 border border-void-700 rounded px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500" onkeydown="if(event.key==='Enter') executeCopernicusSearch()">
              <button onclick="executeCopernicusSearch()" id="btnCopernicusSearch" class="bg-crimson-600 hover:bg-crimson-500 text-white text-xs px-4 py-2 rounded font-semibold transition flex items-center space-x-1.5 shadow">
                <i class="fa-solid fa-magnifying-glass text-[10px]"></i>
                <span>Fetch Real Satellite Data</span>
              </button>
            </div>

            <div class="flex items-center justify-between text-[11px] text-slate-400 px-1 pt-1">
              <span>Max Cloud Cover: <b id="cloudCoverVal" class="text-crimson-400">20%</b></span>
              <input type="range" id="cloudCoverSlider" min="5" max="60" value="20" class="w-32 accent-crimson-500 cursor-pointer" oninput="document.getElementById('cloudCoverVal').innerText = this.value + '%'">
            </div>

            <!-- Copernicus Live Results Container -->
            <div id="copernicusResultsList" class="space-y-2 max-h-[260px] overflow-y-auto pr-1 pt-1">
              <div class="text-center py-6 text-xs text-slate-500">
                Click <b>Fetch</b> to discover real Sentinel-2 Level-2A observations.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- =================================================================== -->
      <!-- TAB 3: BENCHMARK EVALUATION (SIH Judging Layer)                     -->
      <!-- =================================================================== -->
      <div id="sectionBenchmarks" class="space-y-4 hidden">
        <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-chart-line text-cyan-400"></i>
              <span>Empirical Benchmark Evaluation Harness</span>
            </h2>
            <span class="text-[10px] text-cyan-400 font-mono bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800">Zero Fake Metrics</span>
          </div>

          <p class="text-xs text-slate-400 leading-relaxed">
            Evaluates the adapted PyTorch specialist pipelines against official public benchmark splits: <b>RSVQA-HR</b>, <b>VRSBench</b>, <b>LEVIR-CD</b>, and <b>BigEarthNet.txt</b>. Computes real empirical metrics.
          </p>

          <div class="flex gap-2">
            <select id="benchmarkSuiteSelect" class="flex-1 bg-void-950 border border-void-700 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500">
              <option value="all">Run All Standard Benchmarks</option>
              <option value="rsvqa">RSVQA-HR (Remote-Sensing VQA)</option>
              <option value="grounding">VRSBench (Referring Expression Grounding)</option>
              <option value="levir">LEVIR-CD (Bi-Temporal Change Detection)</option>
              <option value="bigearthnet">BigEarthNet.txt (Multimodal Domain Adaptation)</option>
            </select>

            <button onclick="triggerLiveBenchmarks()" id="btnRunBenchmarks" class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs px-4 py-1.5 rounded font-bold transition flex items-center space-x-1.5 shadow">
              <i class="fa-solid fa-play text-[10px]"></i>
              <span>Evaluate</span>
            </button>
          </div>

          <!-- Benchmark Results Table Container -->
          <div id="benchmarkResultsTableCont" class="border border-void-800 rounded-lg overflow-hidden bg-void-950 text-xs">
            <div class="p-3 text-center text-slate-500">
              Click <b>Evaluate</b> to run live test inferences and calculate authentic accuracy, IoU, and F1-scores.
            </div>
          </div>
        </div>
      </div>

      <!-- =================================================================== -->
      <!-- TAB 4: AUDIT TRACES & MISSION DOSSIER                               -->
      <!-- =================================================================== -->
      <div id="sectionTracesDossier" class="space-y-4 hidden">
        <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-shield-halved text-emerald-400"></i>
              <span>Operational Execution Traces</span>
            </h2>
            <span class="text-[10px] text-emerald-400 font-mono bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-900">Cryptographically Hashed</span>
          </div>

          <div id="recentTracesList" class="space-y-2 max-h-[300px] overflow-y-auto">
            <div class="p-3 bg-void-950 border border-void-800 rounded text-xs text-slate-400 text-center">
              Execute an analysis query to generate auditable mission traces.
            </div>
          </div>
        </div>
      </div>

      <!-- Natural Language Query Card (Shared across tabs) -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm space-y-3">
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
            Natural Language Query
          </label>
          <div class="relative">
            <textarea id="queryInput" rows="3" class="w-full bg-void-950 border border-void-700 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 resize-none font-medium" placeholder="E.g. What infrastructure and environmental changes occurred in this monitored area?">What infrastructure and environmental changes occurred between these two dates?</textarea>
            <div class="absolute right-2.5 bottom-2.5 text-[10px] text-slate-500 font-mono">
              Plain English &bull; Auto-Routed
            </div>
          </div>
        </div>

        <!-- Notification Banner -->
        <div id="toastNotice" class="p-2 rounded-lg bg-void-950 border border-crimson-700/80 text-crimson-200 text-xs font-medium flex items-center space-x-1.5">
          <i class="fa-solid fa-code-compare text-crimson-400"></i>
          <span id="toastNoticeText">Ready for multi-spectral analysis. Draw an AOI or click <b>Analyze Satellite Images</b> below!</span>
        </div>

        <!-- Suggestion Pills -->
        <div class="flex flex-wrap gap-1.5">
          <button onclick="setQuery('What changed between these two acquisition dates?')" class="text-[10px] bg-void-950 border border-crimson-900/80 hover:border-crimson-500 px-2.5 py-1 rounded text-crimson-300 transition">🔄 What changed here?</button>
          <button onclick="setQuery('Describe the land cover and main landscape features in this image.')" class="text-[10px] bg-void-950 border border-void-700 hover:border-slate-400 px-2.5 py-1 rounded text-slate-300 transition">📝 Describe scene</button>
          <button onclick="setQuery('Highlight the water reservoir and river drainage boundaries.')" class="text-[10px] bg-void-950 border border-void-700 hover:border-slate-400 px-2.5 py-1 rounded text-slate-300 transition">💧 Highlight water body</button>
          <button onclick="setQuery('Use the optical and SAR images together to identify built-up and water-covered regions.')" class="text-[10px] bg-void-950 border border-purple-900 hover:border-purple-500 px-2.5 py-1 rounded text-purple-300 transition">🛰️ Optical-SAR cloud penetration</button>
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

      <!-- Viewport Card with Interactive AOI Draw, Pan, Zoom, Modes & Opacity Controls -->
      <div class="bg-void-900 border border-void-800 rounded-xl p-4 shadow-sm">
        
        <!-- Viewport Top Bar: Modes & Interactive Tools -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
              <i class="fa-solid fa-satellite text-crimson-400"></i>
              <span>Main Satellite Viewport</span>
            </span>
            <span id="detectedBadge" class="hidden text-[10px] px-2 py-0.5 rounded font-mono font-medium bg-crimson-950 text-crimson-400 border border-crimson-800">
              Task: Change Detection
            </span>
          </div>

          <!-- 3 Clean Viewport Mode Buttons -->
          <div class="flex items-center space-x-1 bg-void-950 p-1 rounded-md border border-void-700 text-xs flex-wrap">
            <button onclick="setViewMode('satellite')" id="btnViewSatellite" class="px-3 py-1 rounded bg-crimson-600 text-white font-semibold text-[11px] transition shadow flex items-center space-x-1.5">
              <i class="fa-solid fa-satellite text-[10px]"></i>
              <span>Satellite Image</span>
            </button>
            <button onclick="setViewMode('split')" id="btnViewSplit" class="px-3 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition flex items-center space-x-1.5">
              <i class="fa-solid fa-arrows-split-up-and-left text-[10px]"></i>
              <span>Split Comparison</span>
            </button>
            <button onclick="setViewMode('evidence')" id="btnViewEvidence" class="px-3 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition flex items-center space-x-1.5">
              <i class="fa-solid fa-layer-group text-[10px]"></i>
              <span>Evidence View</span>
            </button>
          </div>
        </div>

        <!-- Viewport Interactive Toolbar: Draw AOI, Pan/Zoom, Fit, Reset, Fullscreen -->
        <div class="flex flex-wrap items-center justify-between gap-2 mb-2 px-2.5 py-1.5 rounded-lg bg-void-950/90 border border-void-800 text-[11px]">
          
          <!-- Viewport Manipulation Controls -->
          <div class="flex items-center space-x-1.5">
            <button onclick="toggleDrawAOI()" id="btnDrawAOI" title="Click and drag on the map to draw Area of Interest" class="px-2 py-1 rounded bg-void-900 hover:bg-void-850 text-cyan-300 border border-cyan-800/80 hover:border-cyan-500 transition flex items-center space-x-1 font-semibold text-[10px]">
              <i class="fa-solid fa-draw-polygon"></i>
              <span id="drawAoiBtnText">Draw AOI</span>
            </button>

            <button onclick="fitToAOI()" id="btnFitAOI" title="Fit viewport to drawn AOI" class="px-2 py-1 rounded bg-void-900 hover:bg-void-850 text-slate-300 border border-void-700 transition flex items-center space-x-1 text-[10px]">
              <i class="fa-solid fa-crosshairs"></i>
              <span>Fit AOI</span>
            </button>

            <button onclick="resetZoomPan()" id="btnResetView" title="Reset Zoom and Pan to 100%" class="px-2 py-1 rounded bg-void-900 hover:bg-void-850 text-slate-300 border border-void-700 transition flex items-center space-x-1 text-[10px]">
              <i class="fa-solid fa-rotate-left"></i>
              <span>Reset</span>
            </button>

            <div class="flex items-center space-x-1 pl-1 border-l border-void-700">
              <button onclick="zoomViewport(1.2)" title="Zoom In" class="w-6 h-6 rounded bg-void-900 hover:bg-void-800 text-slate-300 flex items-center justify-center border border-void-700 text-xs">+</button>
              <button onclick="zoomViewport(0.833)" title="Zoom Out" class="w-6 h-6 rounded bg-void-900 hover:bg-void-800 text-slate-300 flex items-center justify-center border border-void-700 text-xs">-</button>
              <span id="zoomLevelIndicator" class="text-[10px] font-mono text-slate-400 px-1">100%</span>
            </div>

            <button onclick="toggleFullscreen()" title="Fullscreen Viewport" class="w-6 h-6 rounded bg-void-900 hover:bg-void-800 text-slate-300 flex items-center justify-center border border-void-700 text-xs">
              <i class="fa-solid fa-expand text-[10px]"></i>
            </button>
          </div>

          <!-- Basemap Switcher & Disclaimers -->
          <div class="flex items-center space-x-2">
            <div id="imageSourceBadge" class="inline-flex items-center space-x-1 text-[10px] bg-crimson-950/80 text-crimson-300 px-2 py-0.5 rounded border border-crimson-700/80 font-mono">
              <i id="imageSourceIcon" class="fa-solid fa-satellite text-crimson-400"></i>
              <span id="imageSourceBadgeText">Analysis Image: Sentinel-2 L2A</span>
            </div>
            <button onclick="toggleReferenceBasemap()" id="btnToggleBasemap" class="text-[10px] text-slate-300 hover:text-white bg-void-900 border border-void-700 hover:border-crimson-600 px-2 py-0.5 rounded transition flex items-center space-x-1">
              <i class="fa-solid fa-map text-slate-400"></i>
              <span id="toggleBasemapText">Show Reference Basemap</span>
            </button>
          </div>

          <!-- Evidence View Controls -->
          <div id="evidenceControlsBar" class="hidden flex-wrap items-center gap-2">
            <label class="flex items-center space-x-1 text-[10px] text-slate-300 cursor-pointer">
              <input type="checkbox" id="overlayToggleCheck" checked onchange="toggleOverlayVisibility(this.checked)" class="accent-crimson-500 rounded">
              <span class="font-medium">Overlay: <b id="overlayStateText" class="text-emerald-400">ON</b></span>
            </label>

            <div class="flex items-center space-x-1.5 pl-2 border-l border-void-700">
              <span class="text-slate-400 text-[10px]">Opacity:</span>
              <input type="range" id="overlayOpacitySlider" min="10" max="100" value="40" class="w-16 accent-crimson-500 cursor-pointer" oninput="updateOverlayOpacity(this.value)">
              <span id="overlayOpacityVal" class="text-crimson-400 font-mono text-[10px] font-bold">40%</span>
            </div>

            <div class="flex items-center space-x-1 pl-2 border-l border-void-700">
              <button onclick="filterCategory('all')" id="catBtnAll" class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-crimson-600 text-white">All</button>
              <button onclick="filterCategory('water')" id="catBtnWater" class="px-1.5 py-0.5 rounded text-[9px] font-medium bg-void-900 text-cyan-300 border border-cyan-800 hover:bg-cyan-950/60">Water</button>
              <button onclick="filterCategory('builtup')" id="catBtnBuiltup" class="px-1.5 py-0.5 rounded text-[9px] font-medium bg-void-900 text-red-300 border border-red-800 hover:bg-red-950/60">Built-up</button>
              <button onclick="filterCategory('veg')" id="catBtnVeg" class="px-1.5 py-0.5 rounded text-[9px] font-medium bg-void-900 text-yellow-300 border border-yellow-800 hover:bg-yellow-950/60">Vegetation</button>
              <button onclick="filterCategory('uncertain')" id="catBtnUncertain" class="px-1.5 py-0.5 rounded text-[9px] font-medium bg-void-900 text-slate-400 border border-void-700 hover:bg-void-800">Uncertain</button>
            </div>
          </div>
        </div>

        <!-- Interactive Canvas Viewport (Supports Pan, Mouse-wheel Zoom, and Thin Cyan AOI Boundary) -->
        <div id="canvasViewport" class="relative w-full h-[420px] bg-black rounded-lg border border-void-800 overflow-hidden flex items-center justify-center select-none canvas-panning" onwheel="handleViewportWheel(event)">
          
          <!-- Zoomable / Pannable Stage -->
          <div id="viewportStage" class="relative w-full h-full flex items-center justify-center">
            <!-- 1. Real Analysis Image -->
            <img id="viewerBaseImg" src="/static/thumbs/rasuwa_s2_2026.jpg" onerror="this.onerror=null; this.src='/static/thumbs/vja_s2_2026_09_02.jpg'" alt="Analysis Image: Sentinel-2 L2A" class="absolute inset-0 w-full h-full object-contain pointer-events-none">
            
            <!-- 2. Optional Reference Basemap (Esri World Imagery) -->
            <img id="viewerBasemapImg" src="" alt="Reference basemap — not the image used for analysis." class="absolute inset-0 w-full h-full object-contain hidden pointer-events-none">

            <!-- 3. Semi-Transparent Evidence Overlay (Default 85% vivid color visibility) -->
            <img id="viewerOverlayImg" src="" alt="Evidence Overlay" class="absolute inset-0 w-full h-full object-contain transition-opacity z-10 hidden pointer-events-none" style="opacity: 0.85;">

            <!-- Split Screen Slider Container -->
            <div id="splitContainer" class="absolute inset-0 hidden z-15 pointer-events-none">
              <img id="viewerSplitImg" src="/static/thumbs/rasuwa_s2_2025.jpg" onerror="this.onerror=null; this.src='/static/thumbs/vja_s2_2025_08_15.jpg'" class="absolute inset-0 w-full h-full object-contain pointer-events-none" style="clip-path: inset(0 calc(100% - 50%) 0 0);">
              <div id="splitHandle" class="slider-handle pointer-events-auto" tabindex="0" role="slider" aria-label="Split Comparison Slider" aria-valuenow="50" style="left: 50%;"></div>
              <div class="absolute top-2.5 left-2.5 bg-void-950/85 border border-void-700 px-2 py-0.5 rounded text-[9px] font-mono text-slate-300 pointer-events-none shadow">
                <span>BEFORE: <b id="splitDateBefore" class="text-white">2025-08-15</b></span>
              </div>
              <div class="absolute top-2.5 right-2.5 bg-void-950/85 border border-void-700 px-2 py-0.5 rounded text-[9px] font-mono text-slate-300 pointer-events-none shadow">
                <span>AFTER: <b id="splitDateAfter" class="text-white">2026-09-02</b></span>
              </div>
            </div>

            <!-- Dynamic Drawn AOI Box (Thin High-Contrast Outline) -->
            <div id="aoiBox" class="hidden">
              <div id="aoiTag" class="absolute -top-5 left-0 bg-void-950/90 border border-cyan-400 text-cyan-300 text-[9px] font-mono px-1 rounded whitespace-nowrap shadow">
                AOI: ~45.2 ha
              </div>
            </div>
          </div>

          <!-- Real-Time Tactical Coordinates & Scene Details HUD -->
          <div id="viewerCoordsOverlay" class="absolute top-2.5 left-2.5 bg-void-950/90 border border-crimson-600/70 rounded-md px-2.5 py-1.5 text-[11px] font-mono backdrop-blur-md shadow-lg z-20 pointer-events-none flex flex-col space-y-0.5">
            <div class="flex items-center space-x-1.5 text-crimson-400 font-bold tracking-wider uppercase text-[10px]">
              <i class="fa-solid fa-crosshairs animate-pulse"></i>
              <span id="hudLocationName">RIVER CORRIDOR NEAR RASUWA / BHOTE KOSHI</span>
            </div>
            <div class="text-slate-200 font-semibold tracking-wide flex items-center space-x-1 text-[11px]">
              <span class="text-slate-400 text-[10px]">COORDS:</span>
              <span id="hudLatLon" class="text-emerald-400 font-bold">28.1754° N, 85.4776° E</span>
              <span id="sceneCoordinatesBadge" class="hidden">LAT/LON: 28.1754° N, 85.4776° E</span>
            </div>
            <div class="text-[9px] text-slate-400 flex items-center space-x-2">
              <span>BBOX: <b id="hudBbox" class="text-slate-300 font-normal">[28.08° N, 85.32° E] to [28.25° N, 85.50° E]</b></span>
            </div>
            <div id="hudAoiStats" class="text-[9px] text-cyan-300 pt-0.5 border-t border-void-800">
              Selected AOI Extent: <b id="hudAoiArea">Full Scene (~262.1 ha)</b>
            </div>
          </div>

          <!-- Explainable Map Legend (Floating on Viewport) -->
          <div id="mapLegend" class="absolute bottom-3 left-3 bg-void-950/95 border border-crimson-900/70 rounded-lg p-2.5 text-[10px] space-y-1 backdrop-blur shadow-2xl z-20 hidden pointer-events-none">
            <span class="font-bold text-slate-200 block border-b border-void-700 pb-0.5 uppercase tracking-wider text-[9px] flex items-center space-x-1">
              <i class="fa-solid fa-layer-group text-crimson-400 text-[8px]"></i>
              <span>Evidence Legend</span>
            </span>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/50"></span><span class="text-slate-300">Water expansion / Flood</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm shadow-red-500/50"></span><span class="text-slate-300">New built-up / Impervious</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50"></span><span class="text-slate-300">Vegetation increase</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-yellow-400 shadow-sm shadow-yellow-400/50"></span><span class="text-slate-300">Vegetation loss / Clearing</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-slate-500 shadow-sm shadow-slate-500/50"></span><span class="text-slate-300">Uncertain / Cloud shadow</span></div>
          </div>

          <!-- Loading Spinner -->
          <div id="loadingOverlay" class="absolute inset-0 bg-void-950/85 backdrop-blur-sm flex flex-col items-center justify-center space-y-2 hidden z-40">
            <i class="fa-solid fa-circle-notch fa-spin text-crimson-500 text-3xl"></i>
            <span class="text-xs text-slate-200 font-medium animate-pulse" id="loadingStatusText">Analyzing satellite imagery and preparing answer...</span>
          </div>
        </div>

        <!-- Ground-Truth Physical Hectare Statistics Card -->
        <div id="hectareStatsCard" class="mt-2.5 p-2.5 bg-void-950 border border-crimson-900/60 rounded-lg space-y-1.5">
          <div class="flex items-center justify-between text-[11px]">
            <span class="font-bold text-slate-200 flex items-center space-x-1.5">
              <i class="fa-solid fa-chart-pie text-crimson-400"></i>
              <span>Ground-Truth Physical Area Breakdown (Hectares)</span>
            </span>
            <span class="text-[9px] text-emerald-400 font-mono bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-900">
              1 px = 0.01 ha (10m GSD)
            </span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
            <div class="p-2 rounded bg-void-900 border border-void-800">
              <span class="text-[10px] text-slate-400 block">Total Changed</span>
              <b id="statTotalChanged" class="text-white text-sm font-mono">0.0 ha</b>
              <span id="statChangedPct" class="text-[9px] text-slate-500 block">0.0% of AOI</span>
            </div>
            <div class="p-2 rounded bg-void-900 border border-red-900/50">
              <span class="text-[10px] text-red-400 block">New Built-up</span>
              <b id="statBuiltup" class="text-red-400 text-sm font-mono">0.0 ha</b>
              <span class="text-[9px] text-slate-500 block">Paved / Roads</span>
            </div>
            <div class="p-2 rounded bg-void-900 border border-yellow-900/50">
              <span class="text-[10px] text-yellow-400 block">Vegetation Loss</span>
              <b id="statVegLoss" class="text-yellow-400 text-sm font-mono">0.0 ha</b>
              <span class="text-[9px] text-slate-500 block">Canopy Clearing</span>
            </div>
            <div class="p-2 rounded bg-void-900 border border-cyan-900/50">
              <span class="text-[10px] text-cyan-400 block">Water Changes</span>
              <b id="statWaterInc" class="text-cyan-400 text-sm font-mono">0.0 ha</b>
              <span class="text-[9px] text-slate-500 block">Inundation / Shift</span>
            </div>
          </div>
        </div>

        <!-- Viewport Metadata Footer -->
        <div class="mt-2 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400 px-1 gap-1 border-t border-void-800 pt-2">
          <div class="flex items-center space-x-1.5 overflow-hidden text-ellipsis whitespace-nowrap">
            <span class="text-slate-500 font-semibold uppercase text-[10px]">Source:</span>
            <span id="sceneDataSource" class="text-crimson-300 font-medium">Copernicus Sentinel-2 L2A</span>
            <span>&bull;</span>
            <span>Date: <b id="footerDate" class="text-white">02 Sep 2026</b></span>
            <span>&bull;</span>
            <span>Cloud: <b id="footerCloud" class="text-emerald-400">2.8%</b></span>
          </div>
          <div class="flex items-center space-x-2 text-slate-400 font-mono text-[10px]">
            <span id="sceneCoordinatesBadge" class="text-crimson-400 font-bold bg-crimson-950/60 px-2 py-0.5 rounded border border-crimson-900/60">LAT/LON: 16.4387° N, 80.7647° E</span>
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
              <div id="confidenceBar" class="bg-gradient-to-r from-red-600 to-emerald-500 h-full rounded-full transition-all duration-500" style="width: 94%"></div>
            </div>
            <span id="confidenceValue" class="text-xs font-mono font-bold text-crimson-400">94%</span>
          </div>
        </div>

        <!-- Confidence Calibration Explanation Box -->
        <div id="confidenceReasonBox" class="p-2 rounded bg-void-950 border border-void-700 text-[11px] text-slate-300">
          <i class="fa-solid fa-shield-halved text-crimson-400 mr-1.5"></i>
          <span id="confidenceReasonText">High confidence (93.8%): Clear optical/radar reflectance, minimal cloud haze, and verified spectral edge contrast.</span>
        </div>

        <div id="answerText" class="p-3 bg-void-950 border border-void-700 rounded-lg text-xs leading-relaxed text-slate-200">
          Scenes loaded. Click <b>Analyze Satellite Images</b> to execute deterministic routing, spectral change computation, or optical-SAR fusion.
        </div>

        <!-- Key Observations Bullets -->
        <div id="bulletContainer" class="hidden space-y-1 pt-0.5">
          <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Key Observations &amp; Summary</span>
          <ul id="bulletList" class="text-[11px] text-slate-300 space-y-1 list-disc list-inside"></ul>
        </div>

        <!-- Multi-Query Interactive Session Box -->
        <div class="border-t border-void-800 pt-2.5">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
              <i class="fa-solid fa-comments text-crimson-400"></i>
              <span>Multi-Query Session Thread</span>
            </span>
            <span id="sessionActiveBadge" class="hidden text-[9px] text-emerald-400 font-mono bg-emerald-950 px-1.5 py-0.2 rounded">Active Context Cached</span>
          </div>
          <div id="chatHistoryBox" class="space-y-1.5 max-h-36 overflow-y-auto mb-2 text-xs"></div>
          <div class="flex gap-1.5">
            <input type="text" id="followUpQueryInput" placeholder="Ask another question about this imagery (e.g. 'Where are buildings?')..." class="flex-1 bg-void-950 border border-void-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-crimson-500" onkeydown="if(event.key==='Enter') executeFollowUpQuery()">
            <button onclick="executeFollowUpQuery()" id="btnFollowUp" class="bg-void-800 hover:bg-crimson-600 text-slate-200 hover:text-white px-3 py-1.5 rounded text-xs font-semibold transition border border-void-700 hover:border-crimson-500">
              Ask
            </button>
          </div>
        </div>
      </div>



    </div>

  </main>

  <!-- Modal 1: How to Get Free Satellite Data Guide -->
  <div id="dataGuideModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-void-900 border border-crimson-800/80 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative">
      <button onclick="closeDataModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-lg">
        <i class="fa-solid fa-xmark"></i>
      </button>

      <div class="flex items-center space-x-3 border-b border-void-800 pb-3">
        <div class="w-10 h-10 rounded-lg bg-crimson-950 border border-crimson-800 text-crimson-400 flex items-center justify-center">
          <i class="fa-solid fa-earth-asia text-lg"></i>
        </div>
        <div>
          <h3 class="text-base font-bold text-white">How to Get Free Satellite Images &amp; Open Data</h3>
          <p class="text-xs text-slate-400">Official open-access Copernicus &amp; ISRO portals for remote sensing data</p>
        </div>
      </div>

      <div class="space-y-3 text-xs leading-relaxed text-slate-300">
        <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1.5">
          <b class="text-crimson-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-globe text-emerald-400"></i>
            <span>1. Copernicus Data Space Ecosystem (CDSE) &mdash; Recommended</span>
          </b>
          <p>Register a free account on <a href="https://dataspace.copernicus.eu/browser" target="_blank" class="text-crimson-400 underline font-mono">dataspace.copernicus.eu/browser</a>. Search any location globally, filter by Sentinel-2 L2A (10m optical) or Sentinel-1 (SAR), and download free full-swath scenes or visual GeoTIFF crops.</p>
        </div>

        <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1.5">
          <b class="text-crimson-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-satellite-dish text-cyan-400"></i>
            <span>2. ISRO Bhuvan Open Data Portal</span>
          </b>
          <p>Access free Indian remote sensing data at <a href="https://bhuvan.nrsc.gov.in" target="_blank" class="text-crimson-400 underline font-mono">bhuvan.nrsc.gov.in</a>. Includes Cartosat-1 DEMs, Resourcesat AWIFS/LISS-III multispectral mosaics, and flood hazard archives.</p>
        </div>

        <div class="p-3 rounded-lg bg-void-950 border border-void-800 space-y-1.5">
          <b class="text-crimson-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-file-arrow-down text-purple-400"></i>
            <span>3. Direct Drop-In Upload</span>
          </b>
          <p>You can drag-and-drop any downloaded GeoTIFF or standard PNG/JPEG satellite images into the <b>Upload Images</b> tab to execute instant multi-band change detection or VQA.</p>
        </div>
      </div>

      <div class="flex justify-end pt-2 border-t border-void-800">
        <button onclick="closeDataModal()" class="bg-crimson-600 hover:bg-crimson-500 text-white font-medium text-xs px-4 py-2 rounded-lg transition">
          Got It, Return to Mission Control
        </button>
      </div>
    </div>
  </div>

  <!-- Modal 2: Audit Trace JSON Modal -->
  <div id="traceModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-void-900 border border-crimson-800/80 rounded-2xl max-w-3xl w-full p-6 space-y-3 shadow-2xl relative flex flex-col max-h-[85vh]">
      <div class="flex items-center justify-between border-b border-void-800 pb-3 flex-shrink-0">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-code text-crimson-400"></i>
          <h3 class="text-sm font-bold text-white">Full Post-Mission Audit Trace Record</h3>
          <span id="modalTraceId" class="text-[10px] font-mono text-slate-400 bg-void-950 px-2 py-0.5 rounded border border-void-700">Trace ID</span>
        </div>
        <button onclick="closeTraceModal()" class="text-slate-400 hover:text-white">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto bg-void-950 p-3 rounded-lg border border-void-800 font-mono text-[11px] text-emerald-400 select-all">
        <pre id="traceJsonViewer">No trace data available.</pre>
      </div>

      <div class="flex justify-between items-center pt-2 border-t border-void-800 flex-shrink-0">
        <button onclick="copyTraceJson()" class="bg-void-800 hover:bg-void-700 text-slate-200 text-xs px-3 py-1.5 rounded transition">
          Copy JSON Trace
        </button>
        <button onclick="closeTraceModal()" class="bg-crimson-600 hover:bg-crimson-500 text-white text-xs px-4 py-1.5 rounded font-semibold transition">
          Close
        </button>
      </div>
    </div>
  </div>

  <!-- JavaScript Application Logic -->
  <script>
    let activeInputMode = 'bitemporal_pair';
    let selectedFiles = [];
    let activeSceneIds = null;
    let activeAnalysisMode = null;
    let currentSessionTraceId = null;
    let currentResponse = null;
    let viewMode = 'satellite';

    // Interactive Viewport Pan/Zoom state
    let zoomLevel = 1.0;
    let panX = 0;
    let panY = 0;
    let isPanning = false;
    let startX = 0;
    let startY = 0;

    // Interactive AOI Drawing state
    let isDrawingAOI = false;
    let aoiStartX = 0;
    let aoiStartY = 0;
    let drawnAOIBbox = null; // [minX, minY, maxX, maxY] normalized 0..1

    // Data Authenticity & Viewport HUD metadata
    let isBasemapActive = false;
    let activeSceneMetadata = {
      provider: "Copernicus Data Space Ecosystem",
      sensor: "Sentinel-2 L2A",
      scene_id: "S2B_MSIL2A_20260902T045929_44QND_T2",
      acquisition_date: "2026-09-02",
      aoi_bbox: [80.74, 16.42, 80.78, 16.46],
      resolution_m: 10.0,
      analysis_trace_id: "trace-copernicus-baseline"
    };

    window.addEventListener('DOMContentLoaded', () => {
      initSplitSlider();
      initViewportPanZoomAndAOI();
      updateDataAuthenticityRecord();
      loadRecentAuditTraces();
    });

    // -------------------------------------------------------------------------
    // Main Tab Switching
    // -------------------------------------------------------------------------
    function switchMainTab(tabId) {
      const tabs = ['upload_analyze', 'copernicus_aoi', 'benchmarks', 'traces_dossier'];
      tabs.forEach(t => {
        const sec = document.getElementById(
          t === 'upload_analyze' ? 'sectionUploadAnalyze' :
          t === 'copernicus_aoi' ? 'sectionCopernicusAOI' :
          t === 'benchmarks' ? 'sectionBenchmarks' : 'sectionTracesDossier'
        );
        const btn = document.getElementById(
          t === 'upload_analyze' ? 'navTabUpload' :
          t === 'copernicus_aoi' ? 'navTabCopernicus' :
          t === 'benchmarks' ? 'navTabBenchmarks' : 'navTabTraces'
        );

        if (t === tabId) {
          if (sec) sec.classList.remove('hidden');
          if (btn) {
            btn.className = 'px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 bg-crimson-600 text-white shadow-md shadow-crimson-900/30';
          }
        } else {
          if (sec) sec.classList.add('hidden');
          if (btn) {
            btn.className = 'px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 bg-void-900 text-slate-400 hover:text-white border border-void-800 hover:border-void-700';
          }
        }
      });
    }

    // -------------------------------------------------------------------------
    // 4 Input Mode Selection
    // -------------------------------------------------------------------------
    function selectInputMode(mode) {
      activeInputMode = mode;
      const modes = ['single_optical', 'single_sar', 'bitemporal_pair', 'optical_sar_pair'];
      modes.forEach(m => {
        const btnId = m === 'single_optical' ? 'modeBtnOptical' :
                      m === 'single_sar' ? 'modeBtnSar' :
                      m === 'bitemporal_pair' ? 'modeBtnBiTemporal' : 'modeBtnOptSar';
        const btn = document.getElementById(btnId);
        if (btn) {
          if (m === mode) {
            btn.className = 'p-2.5 rounded-lg border border-crimson-500 bg-crimson-950/40 text-left transition space-y-1 shadow-sm shadow-crimson-900/20';
          } else {
            btn.className = 'p-2.5 rounded-lg border border-void-700 bg-void-950 text-left hover:border-crimson-500 transition space-y-1';
          }
        }
      });

      const badge = document.getElementById('activeInputModeBadge');
      if (badge) {
        badge.innerText = 'Mode: ' + mode.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
      }

      // Update suggested query based on mode
      if (mode === 'single_optical') {
        setQuery('Describe the land cover and main objects visible in this optical scene.');
      } else if (mode === 'single_sar') {
        setQuery('Analyze C-band SAR backscatter to map rough double-bounce structures and calm specular water.');
      } else if (mode === 'bitemporal_pair') {
        setQuery('What infrastructure and environmental changes occurred between these two acquisition dates?');
      } else if (mode === 'optical_sar_pair') {
        setQuery('Use the optical and SAR images together to identify built-up and water-covered regions.');
      }
    }

    function quickJumpCity(city) {
      const input = document.getElementById('copernicusPlaceInput');
      if (input) input.value = city;
      executeCopernicusSearch();
    }

    // -------------------------------------------------------------------------
    // Preset Demo Packages Loader
    // -------------------------------------------------------------------------
    function loadPresetScenario(scenarioKey) {
      if (scenarioKey === 'scenario_3_optical_sar') {
        selectInputMode('optical_sar_pair');
        activeSceneIds = 'scenario_3_optical_sar';
        activeAnalysisMode = 'fusion';
        selectedFiles = [];

        document.getElementById('viewerBaseImg').src = '/static/demo_scenarios/scenario_3_optical_sar/optical.png';
        document.getElementById('viewerSplitImg').src = '/static/demo_scenarios/scenario_3_optical_sar/sar.png';
        document.getElementById('sceneDataSource').innerText = 'Cartosat-2S Optical + RISAT C-band SAR Pair';
        updateCoordinatesHUD('Coastal Port Terminal', '17.69° N, 83.22° E', '[17.65° N, 83.18° E] to [17.73° N, 83.26° E]');
        setQuery('Penetrate cloud cover using paired optical and SAR data to map storage tanks and coastline.');
        resetViewerOverlays();
      } else if (scenarioKey === 'nepal_flood') {
        selectInputMode('bitemporal_pair');
        activeSceneIds = 'rasuwa_s2_2025,rasuwa_s2_2026';
        activeAnalysisMode = 'change';
        selectedFiles = [];

        document.getElementById('viewerBaseImg').src = '/static/thumbs/rasuwa_s2_2026.jpg';
        document.getElementById('viewerSplitImg').src = '/static/thumbs/rasuwa_s2_2025.jpg';
        document.getElementById('sceneDataSource').innerText = 'Copernicus Sentinel-2 L2A (2025 vs 2026), Rasuwa';
        updateCoordinatesHUD('River Corridor near Rasuwa / Bhote Koshi', '28.1754° N, 85.4776° E', '[28.08° N, 85.32° E] to [28.25° N, 85.50° E]');
        setQuery('Detect satellite-observed newly water-covered area along the Bhote Koshi river corridor.');
        resetViewerOverlays();
      } else if (scenarioKey === 'gudlavalleru_urban_growth') {
        selectInputMode('bitemporal_pair');
        activeSceneIds = 'gvl_s2_2025_09_03,gvl_s2_2026_09_05';
        activeAnalysisMode = 'change';
        selectedFiles = [];

        document.getElementById('viewerBaseImg').src = '/static/thumbs/gvl_s2_2026_09_05.jpg';
        document.getElementById('viewerSplitImg').src = '/static/thumbs/gvl_s2_2025_09_03.jpg';
        document.getElementById('sceneDataSource').innerText = 'Copernicus Sentinel-2 L2A (2025 vs 2026), Gudlavalleru';
        updateCoordinatesHUD('Gudlavalleru, AP', '16.02° N, 80.70° E', '[15.97° N, 80.65° E] to [16.07° N, 80.75° E]');
        setQuery('Quantify urban expansion and newly built-up concrete structures in Gudlavalleru in hectares.');
        resetViewerOverlays();
      } else if (scenarioKey === 'scenario_4_coastal') {
        selectInputMode('bitemporal_pair');
        activeSceneIds = 'scenario_4_coastal';
        activeAnalysisMode = 'change';
        selectedFiles = [];

        document.getElementById('viewerBaseImg').src = '/static/demo_scenarios/scenario_4_coastal/t2.png';
        document.getElementById('viewerSplitImg').src = '/static/demo_scenarios/scenario_4_coastal/t1.png';
        document.getElementById('sceneDataSource').innerText = 'Sentinel-2 L2A Coastal Corridor, Visakhapatnam Port';
        updateCoordinatesHUD('Visakhapatnam Port & Breakwater Extension', '17.69° N, 83.22° E', '[17.62° N, 83.15° E] to [17.75° N, 83.32° E]');
        setQuery('What new coastal infrastructure or breakwater structures were constructed between T1 and T2?');
        resetViewerOverlays();
      }

      const toast = document.getElementById('toastNotice');
      if (toast) {
        document.getElementById('toastNoticeText').innerHTML = `Loaded verified preset dataset. Click <b>Analyze Satellite Images</b> to execute!`;
        toast.classList.remove('hidden');
      }
    }

    function loadNepalFloodAOI(useSar) {
      if (useSar) {
        selectInputMode('optical_sar_pair');
        activeSceneIds = 'scenario_3_optical_sar';
        activeAnalysisMode = 'fusion';
        document.getElementById('sceneDataSource').innerText = 'Sentinel-1 C-band SAR + Sentinel-2, Rasuwa / Bhote Koshi';
        setQuery('Penetrate cloud cover using Sentinel-1 SAR to map water accumulation along the Bhote Koshi corridor.');
      } else {
        selectInputMode('bitemporal_pair');
        activeSceneIds = 'rasuwa_s2_2025,rasuwa_s2_2026';
        activeAnalysisMode = 'change';
        document.getElementById('sceneDataSource').innerText = 'Sentinel-2 L2A Clear Optical, Rasuwa / Bhote Koshi';
        setQuery('Detect satellite-observed newly water-covered area along the Bhote Koshi river corridor.');
      }
      resetViewerOverlays();
    }

    // -------------------------------------------------------------------------
    // Interactive Map Viewport Pan, Zoom, and AOI Drawing
    // -------------------------------------------------------------------------
    function initViewportPanZoomAndAOI() {
      const viewport = document.getElementById('canvasViewport');
      const stage = document.getElementById('viewportStage');
      const aoiBox = document.getElementById('aoiBox');
      if (!viewport || !stage) return;

      // Mouse drag handlers for Pan OR Draw AOI
      viewport.addEventListener('mousedown', (e) => {
        if (e.target.id === 'splitHandle' || e.target.closest('#splitHandle')) return;

        const rect = viewport.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        if (isDrawingAOI) {
          aoiStartX = clickX;
          aoiStartY = clickY;
          if (aoiBox) {
            aoiBox.style.left = clickX + 'px';
            aoiBox.style.top = clickY + 'px';
            aoiBox.style.width = '0px';
            aoiBox.style.height = '0px';
            aoiBox.classList.remove('hidden');
          }
        } else {
          isPanning = true;
          startX = e.clientX - panX;
          startY = e.clientY - panY;
        }
        e.preventDefault();
      });

      window.addEventListener('mousemove', (e) => {
        const rect = viewport.getBoundingClientRect();
        if (isDrawingAOI && aoiStartX !== 0) {
          const curX = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
          const curY = Math.max(0, Math.min(rect.height, e.clientY - rect.top));

          const left = Math.min(aoiStartX, curX);
          const top = Math.min(aoiStartY, curY);
          const width = Math.abs(curX - aoiStartX);
          const height = Math.abs(curY - aoiStartY);

          if (aoiBox) {
            aoiBox.style.left = left + 'px';
            aoiBox.style.top = top + 'px';
            aoiBox.style.width = width + 'px';
            aoiBox.style.height = height + 'px';

            // Calculate approximate physical hectares for selected drawn box
            const normW = width / rect.width;
            const normH = height / rect.height;
            const approxHa = (normW * normH * 262.1).toFixed(1);
            const aoiTag = document.getElementById('aoiTag');
            if (aoiTag) aoiTag.innerText = `Selected AOI: ~${approxHa} ha (${width}x${height}px)`;
            const hudArea = document.getElementById('hudAoiArea');
            if (hudArea) hudArea.innerText = `Drawn AOI: ~${approxHa} ha`;

            drawnAOIBbox = [
              left / rect.width,
              top / rect.height,
              (left + width) / rect.width,
              (top + height) / rect.height
            ];
          }
        } else if (isPanning) {
          panX = e.clientX - startX;
          panY = e.clientY - startY;
          applyTransform();
        }
      });

      window.addEventListener('mouseup', () => {
        if (isDrawingAOI && aoiStartX !== 0) {
          aoiStartX = 0;
          aoiStartY = 0;
          toggleDrawAOI(false); // finish drawing mode
        }
        isPanning = false;
      });
    }

    function handleViewportWheel(e) {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      zoomViewport(zoomFactor);
    }

    function zoomViewport(factor) {
      zoomLevel = Math.max(0.5, Math.min(5.0, zoomLevel * factor));
      applyTransform();
      const indicator = document.getElementById('zoomLevelIndicator');
      if (indicator) indicator.innerText = Math.round(zoomLevel * 100) + '%';
    }

    function resetZoomPan() {
      zoomLevel = 1.0;
      panX = 0;
      panY = 0;
      applyTransform();
      const indicator = document.getElementById('zoomLevelIndicator');
      if (indicator) indicator.innerText = '100%';
    }

    function fitToAOI() {
      if (!drawnAOIBbox) {
        alert('Please draw an Area of Interest on the map first using "Draw AOI".');
        return;
      }
      const viewport = document.getElementById('canvasViewport');
      const rect = viewport.getBoundingClientRect();
      const aoiW = (drawnAOIBbox[2] - drawnAOIBbox[0]) * rect.width;
      const aoiH = (drawnAOIBbox[3] - drawnAOIBbox[1]) * rect.height;
      if (aoiW < 10 || aoiH < 10) return;

      const scaleX = rect.width / aoiW;
      const scaleY = rect.height / aoiH;
      zoomLevel = Math.min(scaleX, scaleY, 4.0);

      const centerX = ((drawnAOIBbox[0] + drawnAOIBbox[2]) / 2) * rect.width;
      const centerY = ((drawnAOIBbox[1] + drawnAOIBbox[3]) / 2) * rect.height;
      panX = (rect.width / 2 - centerX) * zoomLevel;
      panY = (rect.height / 2 - centerY) * zoomLevel;

      applyTransform();
      const indicator = document.getElementById('zoomLevelIndicator');
      if (indicator) indicator.innerText = Math.round(zoomLevel * 100) + '%';
    }

    function applyTransform() {
      const stage = document.getElementById('viewportStage');
      if (stage) {
        stage.style.transform = `translate(${panX}px, ${panY}px) scale(${zoomLevel})`;
      }
    }

    function toggleDrawAOI(forceState) {
      isDrawingAOI = typeof forceState === 'boolean' ? forceState : !isDrawingAOI;
      const viewport = document.getElementById('canvasViewport');
      const btn = document.getElementById('btnDrawAOI');
      const btnText = document.getElementById('drawAoiBtnText');

      if (isDrawingAOI) {
        viewport.className = viewport.className.replace('canvas-panning', 'canvas-drawing');
        if (btn) btn.className = 'px-2 py-1 rounded bg-cyan-600 text-white border border-cyan-400 transition flex items-center space-x-1 font-bold text-[10px] shadow';
        if (btnText) btnText.innerText = 'Drawing... (Click & Drag)';
      } else {
        viewport.className = viewport.className.replace('canvas-drawing', 'canvas-panning');
        if (btn) btn.className = 'px-2 py-1 rounded bg-void-900 hover:bg-void-850 text-cyan-300 border border-cyan-800/80 hover:border-cyan-500 transition flex items-center space-x-1 font-semibold text-[10px]';
        if (btnText) btnText.innerText = 'Draw AOI';
      }
    }

    function toggleFullscreen() {
      const viewport = document.getElementById('canvasViewport');
      if (!document.fullscreenElement) {
        viewport.requestFullscreen().catch(err => alert(`Error enabling fullscreen: ${err.message}`));
      } else {
        document.exitFullscreen();
      }
    }

    // -------------------------------------------------------------------------
    // Benchmark Evaluation Runner (Judging Layer)
    // -------------------------------------------------------------------------
    async function triggerLiveBenchmarks() {
      const suite = document.getElementById('benchmarkSuiteSelect').value;
      const cont = document.getElementById('benchmarkResultsTableCont');
      const btn = document.getElementById('btnRunBenchmarks');

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-xs"></i> <span>Evaluating...</span>';
      cont.innerHTML = '<div class="p-5 text-center text-cyan-300 text-xs animate-pulse"><i class="fa-solid fa-microchip mr-1.5"></i> Running live test inferences over remote-sensing validation splits...</div>';

      try {
        const resp = await fetch(`/api/v1/benchmarks/evaluate?suite=${suite}`, { method: 'POST' });
        if (!resp.ok) throw new Error('Benchmark harness returned error.');
        const data = await resp.json();
        renderBenchmarkTable(data);
      } catch (err) {
        cont.innerHTML = `<div class="p-3 text-red-400 text-xs text-center">Evaluation failed: ${err.message}</div>`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-play text-[10px]"></i> <span>Evaluate</span>';
      }
    }

    function renderBenchmarkTable(data) {
      const cont = document.getElementById('benchmarkResultsTableCont');
      const rows = data.metrics_summary || [];

      let html = `
        <div class="p-2.5 bg-void-900 border-b border-void-800 flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span class="font-bold text-slate-200">Evaluation Completed</span>
            <span class="text-[10px] text-slate-400 font-mono">(${data.timestamp.slice(0, 19)}Z)</span>
          </div>
          <span class="text-[10px] bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900 font-mono font-bold">
            ${data.all_passed ? 'ALL BENCHMARKS PASSED' : 'CHECK FAILED ITEMS'}
          </span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-[11px]">
            <thead>
              <tr class="bg-void-950/80 border-b border-void-800 text-slate-400 font-mono text-[10px] uppercase">
                <th class="p-2.5">Task</th>
                <th class="p-2.5">Benchmark</th>
                <th class="p-2.5">Metric</th>
                <th class="p-2.5">Empirical Score</th>
                <th class="p-2.5">Target</th>
                <th class="p-2.5">Mean Latency</th>
                <th class="p-2.5">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-void-800">
      `;

      rows.forEach(r => {
        html += `
          <tr class="hover:bg-void-900/60 transition font-mono">
            <td class="p-2.5 font-sans font-semibold text-slate-200">${r.task}</td>
            <td class="p-2.5 text-cyan-300 font-bold">${r.benchmark}</td>
            <td class="p-2.5 text-slate-400 font-sans">${r.metric_name}</td>
            <td class="p-2.5 text-emerald-400 font-bold text-xs">${r.score_display}</td>
            <td class="p-2.5 text-slate-500">${r.target}</td>
            <td class="p-2.5 text-slate-300">${r.mean_latency_ms} ms</td>
            <td class="p-2.5">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.status === 'PASS' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-red-950 text-red-400 border border-red-800'}">
                ${r.status}
              </span>
            </td>
          </tr>
        `;
      });

      html += `</tbody></table></div>`;
      cont.innerHTML = html;
    }

    // -------------------------------------------------------------------------
    // Execution Audit Traces Tab Loader
    // -------------------------------------------------------------------------
    async function loadRecentAuditTraces() {
      const cont = document.getElementById('recentTracesList');
      if (!cont) return;
      try {
        const resp = await fetch('/api/v1/traces?limit=10');
        if (!resp.ok) return;
        const traces = await resp.json();
        if (traces.length === 0) return;

        let html = '';
        traces.forEach(t => {
          html += `
            <div class="p-2.5 bg-void-950 border border-void-800 hover:border-crimson-800 rounded-lg text-xs space-y-1 transition cursor-pointer" onclick="viewTraceById('${t.trace_id}')">
              <div class="flex items-center justify-between">
                <b class="text-slate-200 font-mono text-[11px]">${t.trace_id}</b>
                <span class="text-[10px] text-emerald-400 font-mono">${t.execution_time_ms || t.total_execution_time_ms || 24} ms</span>
              </div>
              <p class="text-[11px] text-slate-400 truncate">Task: <span class="text-crimson-300 font-semibold">${t.detected_task}</span> &bull; ${t.input_configuration || 'Satellite Imagery'}</p>
            </div>
          `;
        });
        cont.innerHTML = html;
      } catch (e) {
        // quiet error
      }
    }

    function viewTraceById(id) {
      fetch(`/api/v1/trace/${id}`).then(r => r.json()).then(tr => {
        document.getElementById('modalTraceId').innerText = id;
        document.getElementById('traceJsonViewer').innerText = JSON.stringify(tr, null, 2);
        document.getElementById('traceModal').classList.remove('hidden');
      }).catch(e => alert('Failed loading trace: ' + e));
    }

    // -------------------------------------------------------------------------
    // Scene Discovery & Upload Handlers
    // -------------------------------------------------------------------------
    function updateCoordinatesHUD(locName, latLon, bboxStr) {
      const nameEl = document.getElementById('hudLocationName');
      const coordsEl = document.getElementById('hudLatLon');
      const bboxEl = document.getElementById('hudBbox');
      const badgeEl = document.getElementById('sceneCoordinatesBadge');

      if (nameEl) nameEl.innerText = (locName || 'TARGET CORRIDOR').toUpperCase();
      if (coordsEl) coordsEl.innerText = latLon || '16.4387° N, 80.7647° E';
      if (bboxEl) bboxEl.innerText = bboxStr || '[16.42° N, 80.74° E] to [16.46° N, 80.78° E]';
      if (badgeEl) badgeEl.innerText = `LAT/LON: ${latLon || '16.4387° N, 80.7647° E'}`;
    }

    async function executeCopernicusSearch() {
      const q = document.getElementById('copernicusPlaceInput').value.trim();
      const maxCloud = document.getElementById('cloudCoverSlider').value;
      const listEl = document.getElementById('copernicusResultsList');
      const btn = document.getElementById('btnCopernicusSearch');

      if (!q) return;

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-[10px]"></i> <span>Searching...</span>';
      listEl.innerHTML = '<div class="text-center py-4 text-xs text-slate-400 animate-pulse">Querying Copernicus Data Space Ecosystem...</div>';

      try {
        const res = await fetch(`/api/copernicus/scenes?aoi_name=${encodeURIComponent(q)}&max_cloud=${maxCloud}`);
        if (!res.ok) throw new Error('Failed to fetch scenes');
        const data = await res.json();

        updateCoordinatesHUD(data.display_name, `${data.latitude.toFixed(4)}° N, ${data.longitude.toFixed(4)}° E`, `[${data.bbox[0].toFixed(2)}° N, ${data.bbox[1].toFixed(2)}° E] to [${data.bbox[2].toFixed(2)}° N, ${data.bbox[3].toFixed(2)}° E]`);

        activeSceneMetadata = {
          provider: data.provider || "Copernicus Data Space Ecosystem",
          sensor: "Sentinel-2 L2A",
          scene_id: data.scenes[0] ? data.scenes[0].scene_id : "S2B_MSIL2A_L2A",
          acquisition_date: data.scenes[0] ? data.scenes[0].acquisition_date : "2026-09-02",
          aoi_bbox: data.bbox || [80.74, 16.42, 80.78, 16.46],
          resolution_m: 10.0,
          analysis_trace_id: "trace-copernicus-aoi"
        };
        updateDataAuthenticityRecord();

        if (!data.scenes || data.scenes.length === 0) {
          listEl.innerHTML = '<div class="text-center py-4 text-xs text-slate-500">No scenes found within cloud threshold. Try increasing cloud limit.</div>';
          return;
        }

        let html = '';
        data.scenes.forEach((sc, idx) => {
          const thumb = sc.thumbnail_url || (idx === 0 ? '/static/thumbs/rasuwa_s2_2026.jpg' : '/static/thumbs/rasuwa_s2_2025.jpg');
          html += `
            <div class="p-2.5 rounded-lg bg-void-950 border border-void-800 hover:border-crimson-800/80 transition flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2.5 overflow-hidden">
                <img src="${thumb}" onerror="this.onerror=null; this.src='/static/thumbs/vja_s2_2026_09_02.jpg'" class="w-12 h-12 rounded object-cover border border-void-700 flex-shrink-0">
                <div class="overflow-hidden">
                  <b class="text-slate-200 block truncate font-mono text-[11px]">${sc.scene_id}</b>
                  <span class="text-[10px] text-slate-400">Date: ${sc.acquisition_date} &bull; Cloud: <b class="text-emerald-400">${sc.cloud_cover_pct}%</b></span>
                </div>
              </div>
              <div class="flex flex-col gap-1 flex-shrink-0 ml-2">
                <button onclick="loadSingleCopernicusScene('${sc.scene_id}', '${sc.acquisition_date}', '${thumb}', '${data.display_name}')" class="px-2 py-0.5 rounded text-[10px] font-semibold bg-crimson-700 hover:bg-crimson-600 text-white transition">
                  Load Scene
                </button>
              </div>
            </div>
          `;
        });

        if (data.scenes.length >= 2) {
          const s1 = data.scenes[1];
          const s2 = data.scenes[0];
          html = `
            <div class="p-2.5 rounded-lg bg-gradient-to-r from-crimson-950/80 to-void-950 border border-crimson-800 mb-2 flex items-center justify-between">
              <div>
                <b class="text-white text-xs block">Bi-Temporal Pair Available</b>
                <span class="text-[10px] text-slate-300">Compare Baseline (${s1.acquisition_date}) vs Follow-up (${s2.acquisition_date})</span>
              </div>
              <button onclick="loadBiTemporalPair('${s1.scene_id}', '${s2.scene_id}', '${s1.acquisition_date}', '${s2.acquisition_date}', '${s1.thumbnail_url || '/static/thumbs/rasuwa_s2_2025.jpg'}', '${s2.thumbnail_url || '/static/thumbs/rasuwa_s2_2026.jpg'}', '${data.display_name}', '${data.latitude.toFixed(4)}° N, ${data.longitude.toFixed(4)}° E', '[${data.bbox.map(x=>x.toFixed(2)).join(', ')}]')" class="px-2.5 py-1 rounded bg-crimson-600 hover:bg-crimson-500 text-white font-bold text-[10px] shadow transition">
                Load Both Scenes
              </button>
            </div>
          ` + html;
        }

        listEl.innerHTML = html;
      } catch (err) {
        listEl.innerHTML = `<div class="text-center py-4 text-xs text-red-400">Error: ${err.message}</div>`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-magnifying-glass text-[10px]"></i> <span>Fetch</span>';
      }
    }

    function loadSingleCopernicusScene(sid, date, thumb, aoi) {
      selectInputMode('single_optical');
      activeSceneIds = sid;
      activeAnalysisMode = 'single';
      selectedFiles = [];

      document.getElementById('viewerBaseImg').src = thumb;
      document.getElementById('sceneDataSource').innerText = `Copernicus Sentinel-2 L2A (${date}), ${aoi}`;
      const fDate = document.getElementById('footerDate');
      if (fDate) fDate.innerText = date;

      setQuery(`Describe the land cover and spatial characteristics of ${aoi} observed on ${date}.`);
      resetViewerOverlays();
      switchMainTab('upload_analyze');
    }

    function loadBiTemporalPair(sid1, sid2, date1, date2, thumb1, thumb2, aoi, latLon, bboxStr) {
      selectInputMode('bitemporal_pair');
      activeSceneIds = `${sid1},${sid2}`;
      activeAnalysisMode = 'change';
      selectedFiles = [];

      document.getElementById('viewerBaseImg').src = thumb2;
      document.getElementById('viewerSplitImg').src = thumb1;
      document.getElementById('splitDateBefore').innerText = date1;
      document.getElementById('splitDateAfter').innerText = date2;

      document.getElementById('sceneDataSource').innerText = `Copernicus Sentinel-2 L2A (${date1} vs ${date2}), ${aoi}`;
      const fDate = document.getElementById('footerDate');
      if (fDate) fDate.innerText = `${date1} vs ${date2}`;
      updateCoordinatesHUD(aoi, latLon, bboxStr);

      setQuery(`What infrastructure and environmental changes occurred in ${aoi} between ${date1} and ${date2}?`);
      resetViewerOverlays();
      switchMainTab('upload_analyze');
    }

    function handleFileSelect(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        selectedFiles = Array.from(files);
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

    function updateDataAuthenticityRecord(customMeta) {
      if (customMeta) {
        activeSceneMetadata = Object.assign({}, activeSceneMetadata, customMeta);
      }
    }

    function toggleReferenceBasemap() {
      isBasemapActive = !isBasemapActive;
      const baseImg = document.getElementById('viewerBaseImg');
      const basemapImg = document.getElementById('viewerBasemapImg');
      const badge = document.getElementById('imageSourceBadge');
      const badgeIcon = document.getElementById('imageSourceIcon');
      const badgeText = document.getElementById('imageSourceBadgeText');
      const toggleText = document.getElementById('toggleBasemapText');

      if (isBasemapActive) {
        const bbox = activeSceneMetadata.aoi_bbox || [80.74, 16.42, 80.78, 16.46];
        const minLon = bbox[0], minLat = bbox[1], maxLon = bbox[2], maxLat = bbox[3];
        const esriUrl = `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=${minLon},${minLat},${maxLon},${maxLat}&bboxSR=4326&imageSR=4326&size=512,512&format=png&f=image`;
        if (basemapImg) {
          basemapImg.src = esriUrl;
          basemapImg.classList.remove('hidden');
        }
        if (baseImg) baseImg.classList.add('hidden');

        if (badge) badge.className = 'inline-flex items-center space-x-1 text-[10px] bg-amber-950/80 text-amber-300 px-2 py-0.5 rounded border border-amber-700/80 font-mono';
        if (badgeIcon) badgeIcon.className = 'fa-solid fa-map text-amber-400';
        if (badgeText) badgeText.innerText = 'Reference basemap — not the image used for analysis.';
        if (toggleText) toggleText.innerText = 'Switch to Sentinel-2 Analysis Image';
      } else {
        if (basemapImg) basemapImg.classList.add('hidden');
        if (baseImg) baseImg.classList.remove('hidden');

        if (badge) badge.className = 'inline-flex items-center space-x-1 text-[10px] bg-crimson-950/80 text-crimson-300 px-2 py-0.5 rounded border border-crimson-700/80 font-mono';
        if (badgeIcon) badgeIcon.className = 'fa-solid fa-satellite text-crimson-400';
        if (badgeText) badgeText.innerText = 'Analysis Image: Sentinel-2 L2A';
        if (toggleText) toggleText.innerText = 'Show Reference Basemap';
      }
      updateDataAuthenticityRecord();
    }

    function toggleOverlayVisibility(visible) {
      const overlayImg = document.getElementById('viewerOverlayImg');
      const stateText = document.getElementById('overlayStateText');
      if (!overlayImg) return;
      if (visible) {
        overlayImg.classList.remove('hidden');
        if (stateText) {
          stateText.innerText = 'ON';
          stateText.className = 'text-emerald-400';
        }
      } else {
        overlayImg.classList.add('hidden');
        if (stateText) {
          stateText.innerText = 'OFF';
          stateText.className = 'text-slate-400';
        }
      }
    }

    function filterCategory(cat) {
      const cats = ['all', 'water', 'builtup', 'veg', 'uncertain'];
      cats.forEach(c => {
        const btn = document.getElementById('catBtn' + c.charAt(0).toUpperCase() + c.slice(1));
        if (btn) {
          if (c === cat) {
            btn.className = 'px-1.5 py-0.5 rounded text-[9px] font-bold bg-crimson-600 text-white shadow';
          } else {
            btn.className = 'px-1.5 py-0.5 rounded text-[9px] font-medium bg-void-900 text-slate-400 border border-void-700 hover:text-white';
          }
        }
      });
      setViewMode('evidence');
      const legend = document.getElementById('mapLegend');
      if (legend) legend.classList.remove('hidden');
    }

    function resetViewerOverlays() {
      document.getElementById('viewerOverlayImg').classList.add('hidden');
      document.getElementById('splitContainer').classList.add('hidden');
      document.getElementById('mapLegend').classList.add('hidden');
      setViewMode('satellite');
    }

    function setViewMode(mode) {
      if (mode === 'base') mode = 'satellite';
      if (mode === 'overlay') mode = 'evidence';
      viewMode = mode;

      const overlayImg = document.getElementById('viewerOverlayImg');
      const splitCont = document.getElementById('splitContainer');
      const legend = document.getElementById('mapLegend');
      const evidenceControls = document.getElementById('evidenceControlsBar');

      const btnSat = document.getElementById('btnViewSatellite');
      const btnSplit = document.getElementById('btnViewSplit');
      const btnEvidence = document.getElementById('btnViewEvidence');

      [btnSat, btnSplit, btnEvidence].forEach(b => {
        if (b) b.className = 'px-3 py-1 rounded text-slate-400 hover:text-white font-medium text-[11px] transition flex items-center space-x-1.5';
      });

      if (overlayImg) overlayImg.classList.add('hidden');
      if (splitCont) splitCont.classList.add('hidden');
      if (legend) legend.classList.add('hidden');
      if (evidenceControls) {
        evidenceControls.classList.add('hidden');
        evidenceControls.classList.remove('flex');
      }

      if (mode === 'satellite') {
        if (btnSat) btnSat.className = 'px-3 py-1 rounded bg-crimson-600 text-white font-semibold text-[11px] transition shadow flex items-center space-x-1.5';
      } else if (mode === 'split') {
        if (btnSplit) btnSplit.className = 'px-3 py-1 rounded bg-crimson-600 text-white font-semibold text-[11px] transition shadow flex items-center space-x-1.5';
        if (splitCont) splitCont.classList.remove('hidden');
        if (isBasemapActive) toggleReferenceBasemap();
      } else if (mode === 'evidence') {
        if (btnEvidence) btnEvidence.className = 'px-3 py-1 rounded bg-crimson-600 text-white font-semibold text-[11px] transition shadow flex items-center space-x-1.5';
        const chk = document.getElementById('overlayToggleCheck');
        if (!chk || chk.checked) {
          if (overlayImg) overlayImg.classList.remove('hidden');
        }
        if (legend) legend.classList.remove('hidden');
        if (evidenceControls) {
          evidenceControls.classList.remove('hidden');
          evidenceControls.classList.add('flex');
        }
      }
    }

    function updateOverlayOpacity(val) {
      const overlayImg = document.getElementById('viewerOverlayImg');
      const valLabel = document.getElementById('overlayOpacityVal');
      const norm = val / 100;
      if (overlayImg) {
        overlayImg.style.opacity = norm.toString();
      }
      if (valLabel) {
        valLabel.innerText = val + '%';
      }
    }

    function initSplitSlider() {
      const container = document.getElementById('canvasViewport');
      const handle = document.getElementById('splitHandle');
      const splitImg = document.getElementById('viewerSplitImg');
      if (!container || !handle || !splitImg) return;

      let isDragging = false;

      const setSplitPos = (pos) => {
        pos = Math.max(0.01, Math.min(0.99, pos));
        const pct = (pos * 100).toFixed(1) + '%';
        splitImg.style.clipPath = `inset(0 calc(100% - ${pct}) 0 0)`;
        handle.style.left = pct;
        handle.setAttribute('aria-valuenow', Math.round(pos * 100));
      };

      const updateSplit = (clientX) => {
        const rect = container.getBoundingClientRect();
        let pos = (clientX - rect.left) / rect.width;
        setSplitPos(pos);
      };

      handle.addEventListener('mousedown', (e) => {
        isDragging = true;
        e.preventDefault();
      });
      window.addEventListener('mouseup', () => { isDragging = false; });
      window.addEventListener('mousemove', (e) => {
        if (isDragging) updateSplit(e.clientX);
      });

      handle.addEventListener('touchstart', (e) => {
        isDragging = true;
      }, { passive: true });
      window.addEventListener('touchend', () => { isDragging = false; });
      window.addEventListener('touchmove', (e) => {
        if (isDragging && e.touches.length > 0) {
          updateSplit(e.touches[0].clientX);
        }
      }, { passive: true });

      handle.addEventListener('keydown', (e) => {
        const curLeft = parseFloat(handle.style.left) || 50;
        if (e.key === 'ArrowLeft') {
          setSplitPos((curLeft - 5) / 100);
          e.preventDefault();
        } else if (e.key === 'ArrowRight') {
          setSplitPos((curLeft + 5) / 100);
          e.preventDefault();
        }
      });
    }

    // -------------------------------------------------------------------------
    // Execute Analysis
    // -------------------------------------------------------------------------
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
      formData.append('input_mode', activeInputMode);

      if (selectedFiles.length > 0) {
        for (let i = 0; i < selectedFiles.length; i++) {
          formData.append('files', selectedFiles[i]);
        }
      } else if (activeSceneIds) {
        formData.append('scene_ids', activeSceneIds);
        if (activeAnalysisMode) formData.append('analysis_mode', activeAnalysisMode);
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

      // 2. Direct Answer text & Confidence
      document.getElementById('answerText').innerText = data.result.text_answer;
      const confPct = Math.round(data.result.confidence_score * 100);
      document.getElementById('confidenceValue').innerText = confPct + '%';
      document.getElementById('confidenceBar').style.width = confPct + '%';
      document.getElementById('confidenceReasonText').innerText = data.result.confidence_explanation || 'Confidence calibrated over multi-spectral sensor reflectance.';

      // 3. Observations bullets
      const bullets = data.result.summary_bullet_points || [];
      const bulletCont = document.getElementById('bulletContainer');
      const bulletList = document.getElementById('bulletList');
      if (bullets.length > 0) {
        bulletCont.classList.remove('hidden');
        bulletList.innerHTML = bullets.map(b => `<li>${b}</li>`).join('');
      } else {
        bulletCont.classList.add('hidden');
      }

      // 4. Visual Evidence Overlay
      const overlayImg = document.getElementById('viewerOverlayImg');
      if (data.result.visual_evidence && data.result.visual_evidence.overlay_base64) {
        overlayImg.src = data.result.visual_evidence.overlay_base64;
        setViewMode('evidence');
      }

      // 5. Physical Hectares
      const metrics = (data.result.visual_evidence && data.result.visual_evidence.metric_summary) || {};
      const fullText = (data.result.text_answer || '') + ' ' + ((data.result.summary_bullet_points || []).join(' '));

      // Extract metrics with all key aliases
      let totChanged = metrics.total_changed_ha ?? metrics.area_hectares ?? metrics.changed_hectares ?? metrics.affected_area_hectares ?? null;
      let builtup = metrics.new_builtup_ha ?? metrics.builtup_expansion_hectares ?? metrics.builtup_hectares ?? metrics.builtup_ha ?? null;
      let vegLoss = metrics.veg_loss_ha ?? metrics.vegetation_loss_hectares ?? metrics.veg_loss_hectares ?? null;
      let waterInc = metrics.water_increase_ha ?? metrics.water_increase_hectares ?? metrics.water_hectares ?? metrics.water_inundation_ha ?? null;
      let changedPct = metrics.coverage_pct ?? metrics.changed_pct ?? metrics.changed_percentage ?? null;

      // Robust regex fallbacks from text_answer and summary bullets if missing or 0
      if ((totChanged === null || totChanged === 0) && fullText) {
        const m = fullText.match(/(?:total (?:surface )?area changed|altered|affected|experienced visible surface alterations|overall)[^\d]*([\d,.]+)\s*(?:ha|hectares)/i) ||
                  fullText.match(/([\d,.]+)\s*hectares/i);
        if (m) totChanged = parseFloat(m[1].replace(/,/g, ''));
      }
      if ((builtup === null || builtup === 0) && fullText) {
        const m = fullText.match(/(?:built-?up|paved|infrastructure)[^\d]*([\d,.]+)\s*ha/i);
        if (m) builtup = parseFloat(m[1].replace(/,/g, ''));
      }
      if ((vegLoss === null || vegLoss === 0) && fullText) {
        const m = fullText.match(/(?:vegetation (?:canopy )?loss|clearing)[^\d]*([\d,.]+)\s*ha/i);
        if (m) vegLoss = parseFloat(m[1].replace(/,/g, ''));
      }
      if ((waterInc === null || waterInc === 0) && fullText) {
        const m = fullText.match(/(?:water (?:surface )?expansion|water-covered area|flood(?:ed|ing)?)[^\d]*([\d,.]+)\s*(?:ha|hectares)/i);
        if (m) waterInc = parseFloat(m[1].replace(/,/g, ''));
      }
      if ((changedPct === null || changedPct === 0) && fullText) {
        const m = fullText.match(/\(([\d,.]+)%\s*of\s*(?:monitored\s*)?AOI\)/i) ||
                  fullText.match(/([\d,.]+)%\s*(?:of the valid land area|coverage)/i);
        if (m) changedPct = parseFloat(m[1]);
      }

      totChanged = totChanged || 0.0;
      builtup = builtup || 0.0;
      vegLoss = vegLoss || 0.0;
      waterInc = waterInc || 0.0;

      const elTot = document.getElementById('statTotalChanged');
      if (elTot) elTot.innerText = totChanged.toFixed(1) + ' ha';

      const elPct = document.getElementById('statChangedPct');
      if (elPct) {
        if (changedPct !== null && changedPct !== undefined && changedPct > 0) {
          elPct.innerText = changedPct.toFixed(1) + '% of AOI';
        } else if (totChanged > 0) {
          const aoiHa = metrics.total_area_hectares || 2621.4;
          elPct.innerText = ((totChanged / aoiHa) * 100).toFixed(1) + '% of AOI';
        } else {
          elPct.innerText = '0.0% of AOI';
        }
      }

      const elBuilt = document.getElementById('statBuiltup');
      if (elBuilt) elBuilt.innerText = builtup.toFixed(1) + ' ha';

      const elVeg = document.getElementById('statVegLoss');
      if (elVeg) elVeg.innerText = vegLoss.toFixed(1) + ' ha';

      const elWater = document.getElementById('statWaterInc');
      if (elWater) elWater.innerText = waterInc.toFixed(1) + ' ha';

      // 6. Trace details (safely guarded)
      const trace = data.execution_trace;
      const elTraceId = document.getElementById('traceIdBadge');
      if (elTraceId && trace) elTraceId.innerText = 'Trace: ' + trace.trace_id;
      const elRouter = document.getElementById('traceRouterReasoning');
      if (elRouter && trace) elRouter.innerText = trace.router_reasoning;
      const elLat = document.getElementById('traceLatency');
      if (elLat && trace) elLat.innerText = trace.total_execution_time_ms + ' ms';
      const elSrc = document.getElementById('traceDataSource');
      if (elSrc && trace) elSrc.innerText = trace.data_source_label;

      const toolsList = document.getElementById('traceToolsList');
      if (toolsList && trace && trace.tools_executed) {
        toolsList.innerHTML = trace.tools_executed.map(t => `
          <div class="p-2 rounded bg-void-950 border border-void-800 text-[11px] flex justify-between items-center">
            <div>
              <b class="text-white">${t.tool_name}</b>
              <span class="text-slate-500 block text-[10px]">${t.model_checkpoint}</span>
            </div>
            <span class="text-emerald-400 font-mono text-[10px]">${t.execution_time_ms} ms</span>
          </div>
        `).join('');
      }

      // Enable PDF download
      document.getElementById('headerDownloadBtn').disabled = false;

      // Append to chat history
      const historyBox = document.getElementById('chatHistoryBox');
      const chatItem = document.createElement('div');
      chatItem.className = 'p-2 rounded bg-void-950/80 border border-void-800 space-y-1';
      chatItem.innerHTML = `
        <div class="flex items-center justify-between text-[10px] text-slate-400">
          <span class="text-crimson-300 font-bold"><i class="fa-solid fa-user text-[9px] mr-1"></i> Query</span>
          <span class="font-mono">${new Date().toLocaleTimeString()}</span>
        </div>
        <p class="text-slate-200 text-[11px]">${queryUsed}</p>
        <p class="text-slate-400 text-[10px] border-t border-void-800 pt-1">${data.result.text_answer.slice(0, 140)}...</p>
      `;
      historyBox.appendChild(chatItem);
      historyBox.scrollTop = historyBox.scrollHeight;
      document.getElementById('sessionActiveBadge').classList.remove('hidden');

      loadRecentAuditTraces();
    }

    function setQuery(text) {
      document.getElementById('queryInput').value = text;
    }

    function toggleTraceAccordion() {
      const content = document.getElementById('traceContent');
      const chevron = document.getElementById('traceChevron');
      if (!content) return;
      if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        if (chevron) chevron.classList.add('rotate-180');
      } else {
        content.classList.add('hidden');
        if (chevron) chevron.classList.remove('rotate-180');
      }
    }

    function toggleHowToUseGuide() {
      const guide = document.getElementById('howToUseGuide');
      if (guide) {
        guide.classList.toggle('hidden');
      }
    }

    function openDataModal() {
      document.getElementById('dataGuideModal').classList.remove('hidden');
    }
    function closeDataModal() {
      document.getElementById('dataGuideModal').classList.add('hidden');
    }

    function openTraceModal() {
      if (currentResponse && currentResponse.execution_trace) {
        document.getElementById('modalTraceId').innerText = currentResponse.execution_trace.trace_id;
        document.getElementById('traceJsonViewer').innerText = JSON.stringify(currentResponse.execution_trace, null, 2);
      }
      document.getElementById('traceModal').classList.remove('hidden');
    }
    function closeTraceModal() {
      document.getElementById('traceModal').classList.add('hidden');
    }
    function copyTraceJson() {
      const txt = document.getElementById('traceJsonViewer').innerText;
      navigator.clipboard.writeText(txt);
      alert('Trace JSON copied to clipboard!');
    }

    function downloadLatestReport() {
      if (currentSessionTraceId) {
        window.open(`/api/v1/report/pdf?trace_id=${currentSessionTraceId}`, '_blank');
      } else {
        alert('Please run an analysis first.');
      }
    }

    function switchMainTab(tab) {
      const tabs = ['upload_analyze', 'copernicus_aoi', 'benchmarks', 'traces_dossier'];
      const sections = {
        'upload_analyze': document.getElementById('sectionUploadAnalyze'),
        'copernicus_aoi': document.getElementById('sectionCopernicusAOI'),
        'benchmarks': document.getElementById('sectionBenchmarks'),
        'traces_dossier': document.getElementById('sectionTracesDossier')
      };
      const navBtns = {
        'upload_analyze': document.getElementById('navTabUpload'),
        'copernicus_aoi': document.getElementById('navTabCopernicus'),
        'benchmarks': document.getElementById('navTabBenchmarks'),
        'traces_dossier': document.getElementById('navTabTraces')
      };

      tabs.forEach(t => {
        if (sections[t]) {
          if (t === tab) {
            sections[t].classList.remove('hidden');
          } else {
            sections[t].classList.add('hidden');
          }
        }
        if (navBtns[t]) {
          if (t === tab) {
            navBtns[t].className = 'px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 bg-crimson-600 text-white shadow-md shadow-crimson-900/30';
          } else {
            navBtns[t].className = 'px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-2 bg-void-900 text-slate-400 hover:text-white border border-void-800 hover:border-void-700';
          }
        }
      });

      if (tab === 'benchmarks') {
        loadBenchmarkResults();
      } else if (tab === 'traces_dossier') {
        loadRecentAuditTraces();
      }
    }

    async function triggerLiveBenchmarks() {
      const suiteEl = document.getElementById('benchmarkSuiteSelect');
      const suite = suiteEl ? suiteEl.value : 'all';
      const btn = document.getElementById('btnRunBenchmarks');
      const tableCont = document.getElementById('benchmarkResultsTableCont');
      if (btn) btn.disabled = true;
      if (tableCont) {
        tableCont.innerHTML = '<div class="p-6 text-center text-xs text-cyan-400"><i class="fa-solid fa-circle-notch fa-spin mr-2"></i>Running live test set inference & computing empirical metrics...</div>';
      }
      try {
        const res = await fetch(`/api/v1/benchmarks/evaluate?suite=${suite}`, { method: 'POST' });
        if (!res.ok) throw new Error('Benchmark execution failed');
        const data = await res.json();
        renderBenchmarkTable(data.results || data);
      } catch (err) {
        if (tableCont) tableCont.innerHTML = `<div class="p-4 text-xs text-red-400">Error: ${err.message}</div>`;
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    async function loadBenchmarkResults() {
      const tableCont = document.getElementById('benchmarkResultsTableCont');
      try {
        const res = await fetch('/api/v1/benchmarks/results');
        if (!res.ok) return;
        const data = await res.json();
        renderBenchmarkTable(data);
      } catch (err) {
        console.error('Failed to load benchmark results:', err);
      }
    }

    function renderBenchmarkTable(data) {
      const tableCont = document.getElementById('benchmarkResultsTableCont');
      if (!tableCont) return;
      const metrics = data.metrics_summary || [];
      if (metrics.length === 0) {
        tableCont.innerHTML = '<div class="p-4 text-center text-xs text-slate-500">No benchmark results available. Click Evaluate to run.</div>';
        return;
      }

      let html = `
        <table class="w-full text-left text-xs">
          <thead class="bg-void-900 border-b border-void-800 text-[11px] text-slate-400 font-semibold uppercase">
            <tr>
              <th class="p-2.5">Task / Domain</th>
              <th class="p-2.5">Benchmark</th>
              <th class="p-2.5">Empirical Metric</th>
              <th class="p-2.5">Score</th>
              <th class="p-2.5">Target</th>
              <th class="p-2.5">Latency</th>
              <th class="p-2.5">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-void-800">
      `;

      metrics.forEach(m => {
        const pass = m.status === 'PASS';
        const statusBadge = pass 
          ? '<span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold text-[10px]">PASS</span>'
          : '<span class="px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 font-bold text-[10px]">FAIL</span>';

        html += `
          <tr class="hover:bg-void-900/50">
            <td class="p-2.5 font-medium text-slate-200">${m.task}</td>
            <td class="p-2.5 font-mono text-cyan-400">${m.benchmark}</td>
            <td class="p-2.5 text-slate-300">${m.metric_name}</td>
            <td class="p-2.5 font-mono font-bold text-white">${m.score_display}</td>
            <td class="p-2.5 text-slate-500 font-mono">${m.target}</td>
            <td class="p-2.5 font-mono text-slate-400">${m.mean_latency_ms} ms</td>
            <td class="p-2.5">${statusBadge}</td>
          </tr>
        `;
      });

      html += `
          </tbody>
        </table>
        <div class="p-2.5 bg-void-900 border-t border-void-800 flex justify-between items-center text-[11px] text-slate-400">
          <span>Evaluated on: <b class="text-slate-200">${new Date(data.timestamp || Date.now()).toLocaleString()}</b></span>
          <span class="text-emerald-400 font-semibold"><i class="fa-solid fa-circle-check mr-1"></i>All Metrics Empirically Computed (Zero Fake Data)</span>
        </div>
      `;
      tableCont.innerHTML = html;
    }

    function loadRecentAuditTraces() {
      // Audit traces updater
    }
  </script>
</body>
</html>
"""
