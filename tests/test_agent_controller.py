import pytest
import numpy as np
from backend.app.agent.controller import controller

def test_intent_classification_single_vqa():
    task, reasoning = controller.classify_intent(
        query="What type of land cover dominates this scene?",
        image_count=1,
        modalities=["optical"]
    )
    assert task == "visual_question_answering"
    assert "RS_VQA_Specialist" in reasoning

def test_intent_classification_grounding():
    task, reasoning = controller.classify_intent(
        query="Highlight the water reservoir and draw bounding boxes",
        image_count=1,
        modalities=["optical"]
    )
    assert task == "region_grounding"
    assert "Grounding_Specialist" in reasoning

def test_intent_classification_change_detection():
    task, reasoning = controller.classify_intent(
        query="What infrastructure changes occurred between these two dates?",
        image_count=2,
        modalities=["optical", "optical"]
    )
    assert task == "change_detection"
    assert "Siamese_Change_Specialist" in reasoning

def test_intent_classification_optical_sar_fusion():
    task, reasoning = controller.classify_intent(
        query="Penetrate cloud cover to map industrial tanks and coastal water bodies",
        image_count=2,
        modalities=["optical", "sar"]
    )
    assert task == "optical_sar_fusion"
    assert "Optical_SAR_Fusion_Specialist" in reasoning

def test_execution_trace_generation():
    dummy_img = np.zeros((128, 128, 3), dtype=np.uint8)
    dummy_img[:, :] = [50, 150, 50]  # Green terrain
    
    response = controller.execute(
        query="Identify submerged areas",
        images=[dummy_img],
        modalities=["optical"],
        image_names=["test.png"]
    )
    
    assert response.status == "success"
    assert response.execution_trace.trace_id.startswith("trace-sih-26167-")
    assert response.execution_trace.total_execution_time_ms > 0
    assert len(response.execution_trace.tools_executed) >= 1
    tool_names = [t.tool_name for t in response.execution_trace.tools_executed]
    assert "remote_sensing_vqa_tool" in tool_names or "input_validator_tool" in tool_names
    assert response.result.confidence_score >= 0.5
