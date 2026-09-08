from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np
from pydantic import BaseModel

class ToolResult(BaseModel):
    tool_name: str
    task_type: str
    text_output: str
    visual_overlay_b64: Optional[str] = None  # Base64 data URL
    visual_overlay_type: Optional[str] = None  # 'bounding_boxes', 'segmentation_mask', 'change_heatmap', 'fused_overlay'
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    confidence: float
    execution_time_ms: float
    parameters: Dict[str, Any]
    metric_summary: Optional[Dict[str, Any]] = None
    summary_bullet_points: Optional[List[str]] = None

class BaseSpecialistTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the specialist tool."""
        pass

    @property
    @abstractmethod
    def task_type(self) -> str:
        """Category of task handled by this tool."""
        pass

    @property
    @abstractmethod
    def model_checkpoint(self) -> str:
        """Model weight identifier or version string."""
        pass

    @abstractmethod
    def run(
        self,
        images: List[np.ndarray],
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Executes the tool logic and returns standardized ToolResult."""
        pass
