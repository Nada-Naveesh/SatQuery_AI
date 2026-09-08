import pytest
import numpy as np
from backend.app.agent.registry import registry
from backend.app.tools.vqa_tool import RSVqaTool
from backend.app.tools.grounding_tool import TextGuidedGroundingTool
from backend.app.tools.change_tool import BiTemporalChangeTool
from backend.app.tools.fusion_tool import OpticalSARFusionTool

def test_registry_initialization():
    tools = registry.list_tools()
    assert len(tools) == 4
    task_types = [t["task_type"] for t in tools]
    assert "visual_question_answering" in task_types
    assert "region_grounding" in task_types
    assert "change_detection" in task_types
    assert "optical_sar_fusion" in task_types

def test_vqa_tool_execution():
    tool = RSVqaTool()
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [30, 90, 160]  # Water tone
    
    res = tool.run([img], query="Is there water present?")
    assert res.tool_name == "RS_VQA_Specialist_v1"
    assert res.confidence > 0.8
    assert res.visual_overlay_b64 is not None
    assert len(res.summary_bullet_points) > 0

def test_grounding_tool_execution():
    tool = TextGuidedGroundingTool()
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[20:60, 20:60] = [255, 255, 255]  # Salient bright target
    
    res = tool.run([img], query="Highlight the storage structure")
    assert res.tool_name == "Grounding_Specialist_v1"
    assert res.bounding_boxes is not None
    assert len(res.bounding_boxes) >= 1
    assert res.confidence >= 0.85

def test_change_tool_execution():
    tool = BiTemporalChangeTool()
    t1 = np.zeros((100, 100, 3), dtype=np.uint8)
    t2 = t1.copy()
    t2[30:70, 30:70] = [220, 220, 220]  # New concrete building
    
    res = tool.run([t1, t2], query="What changed between these dates?")
    assert res.tool_name == "Siamese_Change_Specialist_v1"
    assert res.visual_overlay_type == "change_heatmap"
    assert res.metric_summary["pixel_count"] > 0

def test_optical_sar_fusion_execution():
    tool = OpticalSARFusionTool()
    opt = np.ones((100, 100, 3), dtype=np.uint8) * 240  # Dense white clouds
    sar = np.random.randint(40, 120, size=(100, 100, 3), dtype=np.uint8)
    sar[40:60, 40:60] = 255  # Bright corner-reflector target
    sar[:, 70:] = 15  # Dark water specular reflection
    
    res = tool.run([opt, sar], query="Penetrate cloud cover to detect tanks")
    assert res.tool_name == "Optical_SAR_Fusion_Specialist_v1"
    assert "penetrated" in res.text_output.lower() or "overcame" in res.text_output.lower()
    assert res.metric_summary["builtup_hectares"] > 0
