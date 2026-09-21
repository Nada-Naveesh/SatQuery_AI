import pytest
import numpy as np
from pathlib import Path

from backend.app.processing.raster_loader import load_raster_scene, RasterScene
from backend.app.processing.alignment import align_scenes, AlignmentResult
from backend.app.processing.cloud_mask import compute_cloud_mask, compute_joint_cloud_mask, CloudMaskResult
from backend.app.processing.indices import compute_spectral_indices, SpectralIndices
from backend.app.processing.change_detection import (
    detect_surface_changes,
    ChangeClassificationResult,
    CLASS_UNCHANGED,
    CLASS_NEW_BUILTUP,
    CLASS_VEG_INCREASE,
    CLASS_VEG_DECREASE,
    CLASS_WATER_INCREASE,
    CLASS_WATER_DECREASE
)
from backend.app.processing.overlay_renderer import render_evidence_overlay
from backend.app.processing.statistics import compute_change_statistics, ChangeStatistics


def test_load_raster_scene():
    # Test 4-band Sentinel-2 array [B02, B03, B04, B08]
    arr4 = np.zeros((100, 100, 4), dtype=np.uint8)
    arr4[:, :, 0] = 50   # Blue
    arr4[:, :, 1] = 100  # Green
    arr4[:, :, 2] = 70   # Red
    arr4[:, :, 3] = 200  # NIR
    scene4 = load_raster_scene(arr4)
    assert scene4.height == 100
    assert scene4.width == 100
    assert scene4.num_channels == 4
    assert scene4.channels == ["B02", "B03", "B04", "B08"]
    assert np.isclose(scene4.blue[0, 0], 50 / 255.0)
    assert np.isclose(scene4.green[0, 0], 100 / 255.0)
    assert np.isclose(scene4.red[0, 0], 70 / 255.0)
    assert np.isclose(scene4.nir[0, 0], 200 / 255.0)


def test_align_scenes_matching():
    arr1 = np.ones((120, 120, 4), dtype=np.uint8) * 80
    arr2 = np.ones((120, 120, 4), dtype=np.uint8) * 100
    sc1 = load_raster_scene(arr1)
    sc2 = load_raster_scene(arr2)
    res = align_scenes(sc1, sc2)
    assert res.aligned_height == 120
    assert res.aligned_width == 120
    assert res.overlap_percentage == 100.0
    assert res.registration_quality == "good"


def test_cloud_masking_physics():
    # Clear pixel: low reflectance in blue
    clear = np.zeros((50, 50, 4), dtype=np.uint8)
    clear[:, :, 0] = 25   # Blue
    clear[:, :, 1] = 75   # Green
    clear[:, :, 2] = 50   # Red
    clear[:, :, 3] = 130  # NIR
    sc_clear = load_raster_scene(clear)

    # Cloudy pixel: high reflectance in blue (> 0.80) and brightness (> 0.88)
    cloud = np.ones((50, 50, 4), dtype=np.uint8) * 245
    sc_cloud = load_raster_scene(cloud)

    mask_res = compute_joint_cloud_mask(sc_clear, sc_cloud)
    assert mask_res.valid_pixel_percentage == 0.0  # Second scene is completely cloudy
    assert mask_res.valid_mask.shape == (50, 50)
    assert np.sum(mask_res.valid_mask) == 0  # All masked out by cloud in scene 2


def test_spectral_indices_calculation():
    # Pure water pixel: high green, low NIR
    water = np.zeros((10, 10, 4), dtype=np.uint8)
    water[:, :, 0] = 80   # Blue
    water[:, :, 1] = 120  # Green
    water[:, :, 2] = 25   # Red
    water[:, :, 3] = 5    # NIR
    sc_water = load_raster_scene(water)
    
    idx_water = compute_spectral_indices(sc_water)
    assert np.all(idx_water.ndwi > 0.5)  # Strong positive NDWI
    assert np.all(idx_water.ndvi < 0.0)   # Negative NDVI for water
    
    # Dense vegetation pixel: low red, high NIR
    veg = np.zeros((10, 10, 4), dtype=np.uint8)
    veg[:, :, 0] = 15   # Blue
    veg[:, :, 1] = 40   # Green
    veg[:, :, 2] = 20   # Red
    veg[:, :, 3] = 200  # NIR
    sc_veg = load_raster_scene(veg)
    
    idx_veg = compute_spectral_indices(sc_veg)
    assert np.all(idx_veg.ndvi > 0.6)   # Strong positive NDVI
    assert np.all(idx_veg.ndwi < -0.4)  # Strong negative NDWI


def test_detect_surface_changes_and_mmu():
    H, W = 100, 100
    # Create T1 (vegetation) and T2 (built-up)
    t1 = np.zeros((H, W, 4), dtype=np.uint8)
    t1[:, :, 0] = 15
    t1[:, :, 1] = 40
    t1[:, :, 2] = 20
    t1[:, :, 3] = 180  # NIR high (veg)

    t2 = t1.copy()
    # Replace a 20x20 block with concrete/built-up (Red high, NIR low)
    t2[20:40, 20:40, 2] = 160  # Red
    t2[20:40, 20:40, 3] = 50   # NIR low

    # Add a single-pixel isolated noise artifact
    t2[80, 80, 2] = 230
    t2[80, 80, 3] = 25

    sc1 = load_raster_scene(t1)
    sc2 = load_raster_scene(t2)
    idx1 = compute_spectral_indices(sc1)
    idx2 = compute_spectral_indices(sc2)
    valid_mask = np.ones((H, W), dtype=bool)

    change_res = detect_surface_changes(sc1, sc2, idx1, idx2, valid_mask, min_mapping_unit_pixels=9)
    
    # 20x20 block = 400 pixels should be detected as built-up
    assert change_res.classified_mask[30, 30] == CLASS_NEW_BUILTUP
    assert np.sum(change_res.builtup_mask) == 400
    
    # The 1-pixel noise artifact at [80, 80] should be filtered out by MMU=9
    assert change_res.classified_mask[80, 80] == CLASS_UNCHANGED


def test_render_evidence_overlay():
    H, W = 64, 64
    t1 = np.ones((H, W, 4), dtype=np.uint8) * 100
    t2 = np.ones((H, W, 4), dtype=np.uint8) * 100
    sc1 = load_raster_scene(t1)
    sc2 = load_raster_scene(t2)
    idx1 = compute_spectral_indices(sc1)
    idx2 = compute_spectral_indices(sc2)
    valid_mask = np.ones((H, W), dtype=bool)

    change_res = detect_surface_changes(sc1, sc2, idx1, idx2, valid_mask)
    # Artificially inject some class pixels for rendering test
    change_res.classified_mask[10:30, 10:30] = CLASS_NEW_BUILTUP
    change_res.classified_mask[35:50, 35:50] = CLASS_WATER_INCREASE
    
    rendered = render_evidence_overlay(sc2.true_color, change_res, alpha=0.85)
    
    assert rendered.rgba_overlay.shape == (H, W, 4)
    assert rendered.blended_image.shape == (H, W, 3)
    assert rendered.rgba_base64.startswith("data:image/png;base64,")
    assert rendered.overlay_base64.startswith("data:image/png;base64,")


def test_compute_change_statistics_and_confidence():
    H, W = 100, 100
    t1 = np.ones((H, W, 4), dtype=np.uint8) * 100
    t2 = np.ones((H, W, 4), dtype=np.uint8) * 100
    sc1 = load_raster_scene(t1)
    sc2 = load_raster_scene(t2)
    idx1 = compute_spectral_indices(sc1)
    idx2 = compute_spectral_indices(sc2)
    valid_mask = np.ones((H, W), dtype=bool)

    change_res = detect_surface_changes(sc1, sc2, idx1, idx2, valid_mask)
    # 300 pixels builtup = 3.0 ha at 10m GSD
    change_res.classified_mask[10:40, 10:20] = CLASS_NEW_BUILTUP

    stats = compute_change_statistics(change_res, resolution_m=10.0, registration_quality="good", overlap_percentage=100.0)
    
    assert np.isclose(stats.changed_area_ha, 3.0)
    assert np.isclose(stats.classes["new_builtup_ha"], 3.0)
    assert np.isclose(stats.area_of_interest_ha, 100.0)
    assert np.isclose(stats.changed_percentage, 3.0)
    assert stats.confidence_score >= 0.85
    assert "3.0 hectares" in stats.simple_explanation
    assert "built-up" in stats.simple_explanation.lower()
