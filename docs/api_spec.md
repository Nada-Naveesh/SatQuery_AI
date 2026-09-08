# SatQuery AI — API Specification (OpenAPI / REST)

**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api/v1`

---

## 1. Health & Registry Status

### `GET /api/v1/health`
Returns system status, active device, and registered specialist remote-sensing tools.

**Response `200 OK`:**
```json
{
  "status": "online",
  "project": "SatQuery AI",
  "ps_id": "26167",
  "organization": "ISRO / Department of Space",
  "device": "cpu",
  "registered_tools": [
    {
      "name": "RS_VQA_Specialist_v1",
      "task_type": "visual_question_answering",
      "model_checkpoint": "bigearthnet-adapted-vqa-vit-base"
    },
    {
      "name": "Grounding_Specialist_v1",
      "task_type": "region_grounding",
      "model_checkpoint": "grounding-dino-rs-fine-tuned"
    },
    {
      "name": "Siamese_Change_Specialist_v1",
      "task_type": "change_detection",
      "model_checkpoint": "changeformer-cdvqa-siamese-base"
    },
    {
      "name": "Optical_SAR_Fusion_Specialist_v1",
      "task_type": "optical_sar_fusion",
      "model_checkpoint": "cross-modal-optical-sar-bigearthnet-vit"
    }
  ]
}
```

---

## 2. Demonstration Scenarios

### `GET /api/v1/scenarios`
Returns pre-configured demonstration scenarios matching SIH evaluation categories.

**Response `200 OK`:**
```json
[
  {
    "id": "scenario_1_flood",
    "title": "Disaster Assessment: Inundation & Submerged Parcels",
    "category": "Single-Image VQA & Grounding",
    "description": "Sentinel-2 optical acquisition over Godavari flood basin...",
    "default_query": "Identify the submerged agricultural parcels and highlight their spatial boundaries.",
    "image_paths": ["/static/samples/flood_sentinel2_optical.png"],
    "input_type": "single"
  },
  {
    "id": "scenario_2_urban",
    "title": "Temporal Change: Urban Sprawl & Infrastructure Expansion",
    "category": "Bi-Temporal Change Analysis (CDVQA)",
    "description": "Pre-construction 2022 vs Post-construction 2024 Sentinel-2 pair...",
    "default_query": "What major infrastructure changes occurred between these two acquisition dates?",
    "image_paths": ["/static/samples/urban_t1_2022.png", "/static/samples/urban_t2_2024.png"],
    "input_type": "bitemporal_pair"
  },
  {
    "id": "scenario_3_optical_sar",
    "title": "All-Weather Fusion: Cloud Penetration (Cartosat + RISAT)",
    "category": "Optical-SAR Cross-Modal Fusion",
    "description": "Cloud-occluded optical image paired with co-registered C-band SAR backscatter...",
    "default_query": "Penetrate cloud cover to map industrial storage tanks and coastal water bodies.",
    "image_paths": ["/static/samples/co_registered_optical_cloudy.png", "/static/samples/co_registered_sar_risat.png"],
    "input_type": "optical_sar_pair"
  }
]
```

---

## 3. Remote Sensing Analysis Endpoint

### `POST /api/v1/analyze`
Submits a natural language query and 1 or 2 satellite imagery scenes (or scenario ID shortcut).

**Form Parameters:**
- `query` (string, required): Natural language prompt.
- `files` (files, optional): Up to 2 satellite imagery files (GeoTIFF/PNG/JPEG).
- `scenario_id` (string, optional): One of `scenario_1_flood`, `scenario_2_urban`, `scenario_3_optical_sar`.
- `task_hint` (string, optional, default="auto"): Explicit task override if desired (`visual_question_answering`, `region_grounding`, `change_detection`, `optical_sar_fusion`).

**Example `curl` Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "query=Identify the submerged agricultural parcels and highlight their spatial boundaries." \
  -F "scenario_id=scenario_1_flood"
```

**Response `200 OK`:**
```json
{
  "status": "success",
  "query": "Identify the submerged agricultural parcels and highlight their spatial boundaries.",
  "detected_task": "visual_question_answering",
  "input_summary": {
    "image_count": 1,
    "modalities": ["optical"],
    "dimensions": [512, 512, 3],
    "crs": "EPSG:4326",
    "resolution_m": 10.0
  },
  "result": {
    "text_answer": "Identified major water/submerged surface coverage across 34.8 hectares (13.3% of the scene extent)...",
    "confidence_score": 0.942,
    "visual_evidence": {
      "evidence_type": "segmentation_mask",
      "overlay_base64": "data:image/png;base64,...",
      "bounding_boxes": null,
      "metric_summary": {
        "pixel_count": 34800,
        "total_pixels": 262144,
        "coverage_percentage": 13.27,
        "area_hectares": 34.8
      }
    },
    "summary_bullet_points": [
      "Water body extent: 34.8 hectares (34800 verified pixels).",
      "Spectral delineation: NDWI response confirms surface water reflectance.",
      "Ground Sampling Distance: 10.0 meters/pixel."
    ]
  },
  "execution_trace": {
    "trace_id": "trace-sih-26167-a4b89c12",
    "timestamp": "2026-09-08T11:20:00.000Z",
    "detected_task": "visual_question_answering",
    "router_reasoning": "Single satellite scene with descriptive or categorical question. Routing to RS_VQA_Specialist.",
    "input_configuration": "1 scene(s) [optical]",
    "tools_executed": [
      {
        "tool_name": "RS_VQA_Specialist_v1",
        "task_type": "visual_question_answering",
        "model_checkpoint": "bigearthnet-adapted-vqa-vit-base",
        "parameters": {"query_target": "identify submerged...", "spectral_bands": "RGB/VNIR"},
        "execution_time_ms": 18.2,
        "confidence": 0.942
      }
    ],
    "total_execution_time_ms": 22.4
  },
  "report_download_url": "/api/v1/report/pdf?trace_id=trace-sih-26167-a4b89c12"
}
```

---

## 4. Download PDF Mission Report

### `GET /api/v1/report/pdf?trace_id={trace_id}`
Returns a generated 2-page intelligence report as a binary PDF file.

**Response `200 OK`:**
- `Content-Type`: `application/pdf`
- `Content-Disposition`: `attachment; filename="SatQuery_MissionReport_{trace_id}.pdf"`
