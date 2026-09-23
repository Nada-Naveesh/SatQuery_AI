import time
from typing import Dict, Any, List, Optional
import numpy as np

from backend.app.tools.base_tool import BaseSpecialistTool, ToolResult
from backend.app.utils.report_generator import generate_mission_pdf_report

class ReportGeneratorTool(BaseSpecialistTool):
    """
    Automated Mission PDF Report Generator Specialist (SIH 2026 PS 26167).
    Compiles input summaries, spectral analysis results, evidence overlays,
    confidence metrics, and auditable cryptographic trace hashes into a formal PDF dossier.
    """
    @property
    def name(self) -> str:
        return "report_generator_tool"

    @property
    def task_type(self) -> str:
        return "report_generation"

    @property
    def model_checkpoint(self) -> str:
        return "reportlab-pdf-mission-engine-v2"

    def run(
        self,
        images: List[np.ndarray],
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        start_t = time.perf_counter()
        params = parameters or {}
        trace_id = params.get("trace_id", "trace-live")
        query_text = query or params.get("query", "Remote Sensing Mission Query")
        detected_task = params.get("detected_task", "multimodal_analysis")
        tool_records = params.get("tools_executed", [])
        evidence_b64 = params.get("visual_overlay_b64")
        summary_bullets = params.get("summary_bullet_points", [])
        stats = params.get("metric_summary", {})

        pdf_bytes = generate_mission_pdf_report(
            trace_id=trace_id,
            query=query_text,
            detected_task=detected_task,
            tool_records=tool_records,
            visual_evidence_b64=evidence_b64,
            summary_bullet_points=summary_bullets,
            statistics=stats
        )

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        pdf_size_kb = len(pdf_bytes) / 1024.0

        return ToolResult(
            tool_name=self.name,
            task_type=self.task_type,
            text_output=f"Mission intelligence PDF dossier generated successfully ({pdf_size_kb:.1f} KB). Trace ID: {trace_id}.",
            visual_overlay_b64=None,
            confidence=0.99,
            execution_time_ms=round(elapsed_ms, 2),
            parameters={
                "trace_id": trace_id,
                "pdf_size_bytes": len(pdf_bytes),
                "download_url": f"/api/v1/report/pdf?trace_id={trace_id}"
            },
            metric_summary={
                "pdf_size_kb": round(pdf_size_kb, 1),
                "is_compiled": 1.0
            },
            summary_bullet_points=[
                f"Mission Report: {pdf_size_kb:.1f} KB PDF compiled.",
                f"Trace Verification: {trace_id}",
                "Includes spectral metrics, visual evidence overlay, and audit logs."
            ]
        )
