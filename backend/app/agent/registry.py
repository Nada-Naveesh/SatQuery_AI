from typing import Dict, Any, List, Optional
from backend.app.tools.base_tool import BaseSpecialistTool
from backend.app.tools.vqa_tool import RSVqaTool
from backend.app.tools.caption_tool import SceneCaptionTool
from backend.app.tools.grounding_tool import TextGuidedGroundingTool
from backend.app.tools.change_tool import BiTemporalChangeTool
from backend.app.tools.fusion_tool import OpticalSARFusionTool
from backend.app.tools.input_validator_tool import InputValidatorTool
from backend.app.tools.report_tool import ReportGeneratorTool

class SpecialistToolRegistry:
    """
    Central registry for all remote-sensing specialist tools (SIH 2026 PS 26167).
    Guarantees deterministic routing and eliminates hallucinated tool calls.
    """
    def __init__(self):
        self._tools: Dict[str, BaseSpecialistTool] = {}
        self._task_map: Dict[str, BaseSpecialistTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        tools = [
            InputValidatorTool(),
            RSVqaTool(),
            SceneCaptionTool(),
            TextGuidedGroundingTool(),
            BiTemporalChangeTool(),
            OpticalSARFusionTool(),
            ReportGeneratorTool(),
        ]
        for t in tools:
            self.register(t)
        # Canonical & flexible task routing aliases
        self._task_map["bi_temporal_change_detection"] = self.get_tool_by_task("change_detection")
        self._task_map["temporal_change"] = self.get_tool_by_task("change_detection")
        self._task_map["vqa"] = self.get_tool_by_task("visual_question_answering")
        self._task_map["single_image_vqa"] = self.get_tool_by_task("visual_question_answering")
        self._task_map["captioning"] = self.get_tool_by_task("scene_captioning")
        self._task_map["caption"] = self.get_tool_by_task("scene_captioning")
        self._task_map["grounding"] = self.get_tool_by_task("region_grounding")
        self._task_map["text_guided_grounding"] = self.get_tool_by_task("region_grounding")
        self._task_map["fusion"] = self.get_tool_by_task("optical_sar_fusion")
        self._task_map["validation"] = self.get_tool_by_task("input_validation")
        self._task_map["report"] = self.get_tool_by_task("report_generation")

    def register(self, tool: BaseSpecialistTool):
        self._tools[tool.name] = tool
        self._task_map[tool.task_type] = tool

    def get_tool_by_name(self, name: str) -> Optional[BaseSpecialistTool]:
        return self._tools.get(name)

    def get_tool_by_task(self, task_type: str) -> Optional[BaseSpecialistTool]:
        return self._task_map.get(task_type)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "task_type": t.task_type,
                "model_checkpoint": t.model_checkpoint,
            }
            for t in self._tools.values()
        ]

registry = SpecialistToolRegistry()
