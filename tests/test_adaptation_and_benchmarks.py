import pytest
import os
import torch
import numpy as np
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.models.adaptation.adapter import MultimodalRSAdapter, get_adapted_model
from backend.app.tools.input_validator_tool import InputValidatorTool
from backend.app.agent.controller import controller

client = TestClient(app)

def test_multimodal_rs_adapter_instantiation_and_weights():
    """
    Verifies that MultimodalRSAdapter initializes properly and loads the trained BigEarthNet weights.
    """
    adapter = get_adapted_model()
    assert adapter is not None
    assert isinstance(adapter, MultimodalRSAdapter)
    
    # Verify trained weights file exists
    weights_path = os.path.join(
        os.path.dirname(__file__), "..", "backend", "app", "models", "adaptation", "bigearthnet_adapter.pt"
    )
    assert os.path.exists(weights_path), f"Trained weights not found at {weights_path}"
    assert os.path.getsize(weights_path) > 100_000, "Weights file should be > 100 KB"

def test_multimodal_rs_adapter_forward_and_prediction():
    """
    Verifies dual-stream optical + SAR forward pass and land cover multi-label prediction.
    """
    adapter = get_adapted_model()
    adapter.eval()
    
    # 1. Forward pass with synthetic optical (B=1, C=3, H=128, W=128) and SAR (B=1, C=2, H=128, W=128)
    opt = torch.randn(1, 3, 128, 128)
    sar = torch.randn(1, 2, 128, 128)
    
    with torch.no_grad():
        logits, fused_norm = adapter(opt, sar)
        assert logits.shape == (1, 19)
        assert fused_norm.shape == (1, 256)

    # 2. predict_land_cover helper with NumPy imagery
    opt_np = np.random.randint(10, 200, (128, 128, 3), dtype=np.uint8)
    sar_np = np.random.randint(10, 200, (128, 128, 2), dtype=np.uint8)
    preds = adapter.predict_land_cover(opt_np, sar_np)
    assert isinstance(preds, dict)
    assert "top_classes" in preds
    for item in preds["top_classes"]:
        assert "class_name" in item
        assert "probability" in item
        assert 0.0 <= item["probability"] <= 1.0

def test_input_validator_accepts_valid_geotiff_mode():
    """
    Verifies that InputValidatorTool accepts valid modes and valid images.
    """
    validator = InputValidatorTool()
    
    # Mode: single_optical
    valid_img = np.random.randint(10, 200, (256, 256, 3), dtype=np.uint8)
    res = validator.validate_inputs(
        images=[valid_img],
        input_mode="single_optical",
        filenames=["sentinel2_l2a.tif"],
    )
    assert res["is_valid"] is True
    assert res["input_mode"] == "single_optical"
    assert res["image_count"] == 1

    tool_res = validator.run(
        images=[valid_img],
        parameters={"input_mode": "single_optical"}
    )
    assert tool_res.confidence == 0.99
    assert tool_res.metric_summary["is_valid"] == 1.0

def test_input_validator_rejects_empty_or_corrupt_input():
    """
    Verifies that InputValidatorTool gatekeeper rejects corrupt, blank, or improperly paired images.
    """
    validator = InputValidatorTool()
    
    # 1. Blank/Empty image
    blank_img = np.zeros((100, 100, 3), dtype=np.uint8)
    res_blank = validator.validate_inputs(
        images=[blank_img],
        input_mode="single_optical",
    )
    assert res_blank["is_valid"] is False
    assert any("blank" in err.lower() or "uniform" in err.lower() for err in res_blank["errors"])

    # 2. Bi-temporal missing 2nd scene
    valid_a = np.random.randint(10, 200, (128, 128, 3), dtype=np.uint8)
    res_missing = validator.validate_inputs(
        images=[valid_a],
        input_mode="bitemporal_pair",
    )
    assert res_missing["is_valid"] is False
    assert any("requires 2" in err.lower() for err in res_missing["errors"])

    # 3. Invalid date ordering (T1 >= T2)
    valid_b = np.random.randint(10, 200, (128, 128, 3), dtype=np.uint8)
    res_date = validator.validate_inputs(
        images=[valid_a, valid_b],
        input_mode="bitemporal_pair",
        metadata={"date_before": "2026-09-02", "date_after": "2025-08-15"},
    )
    assert res_date["is_valid"] is False
    assert any("date" in err.lower() for err in res_date["errors"])

def test_agent_controller_stops_early_on_invalid_input():
    """
    Verifies that the Agentic Controller does NOT execute models when input validation fails,
    providing full audit trace of the rejection.
    """
    blank_img = np.zeros((64, 64, 3), dtype=np.uint8)
    
    resp = controller.execute(
        query="What changed between these images?",
        images=[blank_img],
        modalities=["optical"],
        image_names=["blank.png"],
        task_hint="single_optical",
    )
    assert resp.status == "rejected"
    assert "input validation" in resp.result.text_answer.lower()
    trace = resp.execution_trace
    assert trace.tools_executed[0].tool_name == "input_validator_tool"
    assert trace.tools_executed[0].confidence == 0.0
    # Downstream specialists must be skipped on validation rejection
    assert len(trace.tools_executed) == 1

def test_benchmark_api_results_and_evaluation():
    """
    Verifies the /api/v1/benchmarks/results and /api/v1/benchmarks/evaluate endpoints.
    """
    # 1. Fetch existing benchmark results
    res = client.get("/api/v1/benchmarks/results")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert "metrics_summary" in data
    assert data["total_benchmarks_evaluated"] >= 1
    
    # 2. Trigger live evaluation of BigEarthNet suite on demand
    eval_res = client.post("/api/v1/benchmarks/evaluate?suite=bigearthnet")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["status"] == "completed"
    assert "metrics_summary" in eval_data
    assert len(eval_data["metrics_summary"]) >= 1
