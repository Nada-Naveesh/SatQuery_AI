import pytest
import numpy as np
from backend.app.agent.registry import registry
from backend.app.tools.vqa_tool import RSVqaTool
from backend.app.tools.caption_tool import SceneCaptionTool
from backend.app.tools.grounding_tool import TextGuidedGroundingTool
from backend.app.tools.change_tool import BiTemporalChangeTool
from backend.app.tools.fusion_tool import OpticalSARFusionTool
from backend.app.tools.input_validator_tool import InputValidatorTool
from backend.app.tools.report_tool import ReportGeneratorTool

def test_registry_initialization():
    tools = registry.list_tools()
    assert len(tools) == 7
    task_types = [t["task_type"] for t in tools]
    assert "input_validation" in task_types
    assert "visual_question_answering" in task_types
    assert "scene_captioning" in task_types
    assert "region_grounding" in task_types
    assert "change_detection" in task_types
    assert "optical_sar_fusion" in task_types
    assert "report_generation" in task_types

def test_vqa_tool_execution():
    tool = RSVqaTool()
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [30, 90, 160]  # Water tone
    
    res = tool.run([img], query="Is there water present?")
    assert res.tool_name == "remote_sensing_vqa_tool"
    assert res.confidence > 0.8
    assert res.visual_overlay_b64 is not None
    assert len(res.summary_bullet_points) > 0

def test_caption_tool_execution():
    tool = SceneCaptionTool()
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = [45, 140, 55]  # Vegetation
    
    res = tool.run([img], query="Describe the scene and land cover")
    assert res.tool_name == "scene_caption_tool"
    assert res.task_type == "scene_captioning"
    assert "coverage" in res.text_output.lower() or "vegetated" in res.text_output.lower()
    assert res.visual_overlay_b64 is not None

def test_grounding_tool_execution():
    tool = TextGuidedGroundingTool()
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[20:60, 20:60] = [255, 255, 255]  # Salient bright target
    
    res = tool.run([img], query="Highlight the storage structure")
    assert res.tool_name == "text_guided_grounding_tool"
    assert res.bounding_boxes is not None
    assert len(res.bounding_boxes) >= 1
    assert res.confidence >= 0.85

def test_change_tool_execution():
    tool = BiTemporalChangeTool()
    t1 = np.zeros((100, 100, 3), dtype=np.uint8)
    t2 = t1.copy()
    t2[30:70, 30:70] = [220, 220, 220]  # New concrete building
    
    res = tool.run([t1, t2], query="What changed between these dates?")
    assert res.tool_name == "temporal_change_tool"
    assert res.visual_overlay_type == "change_heatmap"
    assert res.metric_summary["pixel_count"] > 0

def test_optical_sar_fusion_execution():
    tool = OpticalSARFusionTool()
    opt = np.ones((100, 100, 3), dtype=np.uint8) * 240  # Dense white clouds
    sar = np.random.randint(40, 120, size=(100, 100, 3), dtype=np.uint8)
    sar[40:60, 40:60] = 255  # Bright corner-reflector target
    sar[:, 70:] = 15  # Dark water specular reflection
    
    res = tool.run([opt, sar], query="Penetrate cloud cover to detect tanks")
    assert res.tool_name == "optical_sar_fusion_tool"
    assert "penetrated" in res.text_output.lower() or "overcame" in res.text_output.lower() or "clouds" in res.text_output.lower()
    assert res.metric_summary["builtup_hectares"] > 0

def test_input_validator_tool_execution():
    tool = InputValidatorTool()
    valid_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    # Valid single scene
    res_valid = tool.run([valid_img], parameters={"input_mode": "single_optical", "filenames": ["scene1.tif"]})
    assert res_valid.confidence > 0.9
    assert res_valid.parameters["validation_errors"] == []
    
    # Invalid zero image
    blank_img = np.zeros((100, 100, 3), dtype=np.uint8)
    res_invalid = tool.run([blank_img], parameters={"input_mode": "single_optical", "filenames": ["blank.tif"]})
    assert res_invalid.confidence == 0.0
    assert len(res_invalid.parameters["validation_errors"]) > 0
