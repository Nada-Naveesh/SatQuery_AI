from typing import Dict, Any, List, Optional
from backend.app.tools.base_tool import BaseSpecialistTool
from backend.app.tools.vqa_tool import RSVqaTool
from backend.app.tools.grounding_tool import TextGuidedGroundingTool
from backend.app.tools.change_tool import BiTemporalChangeTool
from backend.app.tools.fusion_tool import OpticalSARFusionTool

class SpecialistToolRegistry:
    """
    Central registry for all remote-sensing specialist tools.
    Guarantees deterministic routing and eliminates hallucinated tool calls.
    """
    def __init__(self):
        self._tools: Dict[str, BaseSpecialistTool] = {}
        self._task_map: Dict[str, BaseSpecialistTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        tools = [
            RSVqaTool(),
            TextGuidedGroundingTool(),
            BiTemporalChangeTool(),
            OpticalSARFusionTool(),
        ]
        for t in tools:
            self.register(t)
        # Aliases for flexible task routing
        self._task_map["bi_temporal_change_detection"] = self.get_tool_by_task("change_detection")
        self._task_map["vqa"] = self.get_tool_by_task("visual_question_answering")
        self._task_map["grounding"] = self.get_tool_by_task("region_grounding")
        self._task_map["fusion"] = self.get_tool_by_task("optical_sar_fusion")

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
