import time
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from backend.app.agent.registry import registry
from backend.app.schemas import (
    AnalysisResponse,
    AnalysisResult,
    ExecutionTrace,
    ToolExecutionRecord,
    InputSummary,
    VisualEvidence,
    BoundingBox,
)
from backend.app.tools.base_tool import ToolResult

class AgenticController:
    """
    Core Agentic Orchestrator for SatQuery AI.
    Analyzes natural language queries and input image geometry to construct
    an execution graph, invoke specialist models from the registry, and log
    auditable execution traces without hallucination.
    """
    def __init__(self):
        self.registry = registry

    def classify_intent(
        self,
        query: str,
        image_count: int,
        modalities: List[str],
        task_hint: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Determines the specialist task and generates transparent routing reasoning.
        Returns: (task_type, reasoning_explanation)
        """
        q = (query or "").lower().strip()
        
        # Check for explicit hint override
        if task_hint and task_hint != "auto":
            return task_hint, f"Explicit user task override specified: '{task_hint}'."

        # Rule 1: Optical + SAR cross-modal pair detection
        has_sar = any("sar" in m.lower() for m in modalities)
        has_opt = any("optical" in m.lower() or "multispectral" in m.lower() for m in modalities)
        if image_count == 2 and has_sar and has_opt:
            return (
                "optical_sar_fusion",
                "Detected co-registered Optical + SAR image pair. Routing to Optical_SAR_Fusion_Specialist for cross-modal structural/dielectric reasoning."
            )

        # Rule 2: Bi-temporal pair detection
        if image_count == 2:
            return (
                "change_detection",
                "Detected 2 temporal acquisition scenes. Routing to Siamese_Change_Specialist for bi-temporal delta computation and change-VQA."
            )

        # Query semantics for temporal change (even if 2 images passed without explicit labels)
        if any(w in q for w in ["change", "difference", "between", "expansion", "growth", "before and after", "temporal"]):
            if image_count >= 2:
                return (
                    "change_detection",
                    "Query explicitly requests temporal change analysis over multi-date image pair."
                )

        # Query semantics for Optical-SAR fusion / cloud penetration
        if any(w in q for w in ["penetrate", "cloud", "sar", "radar", "cross-modal", "fusion", "all-weather"]):
            if image_count >= 2:
                return (
                    "optical_sar_fusion",
                    "Query requests cross-modal all-weather radar/optical fusion."
                )

        # Rule 3: Text-guided Grounding / Localization
        grounding_verbs = ["highlight", "locate", "where is", "find the", "draw bounding", "bounding box", "isolate", "detect all"]
        if any(gv in q for gv in grounding_verbs):
            return (
                "region_grounding",
                f"Query contains referring expression / spatial localization directive. Routing to Grounding_Specialist for bounding box extraction."
            )

        # Rule 4: Default single-image VQA
        return (
            "visual_question_answering",
            "Single satellite scene with descriptive or categorical question. Routing to RS_VQA_Specialist."
        )

    def execute(
        self,
        query: str,
        images: List[np.ndarray],
        modalities: List[str],
        image_names: List[str],
        task_hint: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> AnalysisResponse:
        total_start_t = time.perf_counter()
        trace_id = f"trace-sih-26167-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        image_count = len(images)
        task_type, reasoning = self.classify_intent(query, image_count, modalities, task_hint)

        # Lookup tool in registry
        tool = self.registry.get_tool_by_task(task_type)
        if tool is None:
            # Fallback to RS-VQA
            tool = self.registry.get_tool_by_task("visual_question_answering")
            task_type = "visual_question_answering"
            reasoning += " (Fallback tool invoked as requested task tool was unavailable)"

        # Execute the specialist tool
        tool_result: ToolResult = tool.run(images=images, query=query, parameters=parameters)

        # Calculate execution telemetry
        total_elapsed_ms = (time.perf_counter() - total_start_t) * 1000.0

        tool_record = ToolExecutionRecord(
            tool_name=tool_result.tool_name,
            task_type=tool_result.task_type,
            model_checkpoint=tool.model_checkpoint,
            parameters=tool_result.parameters,
            execution_time_ms=tool_result.execution_time_ms,
            confidence=tool_result.confidence
        )

        h, w = images[0].shape[:2]
        input_summary = InputSummary(
            image_count=image_count,
            modalities=modalities,
            dimensions=[w, h, images[0].shape[2] if images[0].ndim == 3 else 1],
            crs="EPSG:4326",
            resolution_m=10.0
        )

        # Format visual evidence
        visual_evidence = None
        if tool_result.visual_overlay_b64:
            boxes = None
            if tool_result.bounding_boxes:
                boxes = [
                    BoundingBox(
                        label=b.get("label", "Target"),
                        xmin=b["xmin"],
                        ymin=b["ymin"],
                        xmax=b["xmax"],
                        ymax=b["ymax"],
                        score=b.get("score", 1.0)
                    )
                    for b in tool_result.bounding_boxes
                ]

            visual_evidence = VisualEvidence(
                evidence_type=tool_result.visual_overlay_type or "overlay",
                overlay_base64=tool_result.visual_overlay_b64,
                bounding_boxes=boxes,
                metric_summary=tool_result.metric_summary
            )

        execution_trace = ExecutionTrace(
            trace_id=trace_id,
            timestamp=timestamp,
            detected_task=task_type,
            router_reasoning=reasoning,
            input_configuration=f"{image_count} scene(s) [{', '.join(modalities)}]",
            tools_executed=[tool_record],
            total_execution_time_ms=round(total_elapsed_ms, 2)
        )

        result = AnalysisResult(
            text_answer=tool_result.text_output,
            confidence_score=tool_result.confidence,
            visual_evidence=visual_evidence,
            summary_bullet_points=tool_result.summary_bullet_points
        )

        return AnalysisResponse(
            status="success",
            query=query,
            detected_task=task_type,
            input_summary=input_summary,
            result=result,
            execution_trace=execution_trace,
            report_download_url=f"/api/v1/report/pdf?trace_id={trace_id}"
        )

controller = AgenticController()
