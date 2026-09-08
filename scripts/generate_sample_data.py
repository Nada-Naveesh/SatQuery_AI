import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "backend" / "static" / "samples"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_scenario_1():
    """
    Scenario 1: Single Optical Image (Sentinel-2) - Flooded Agricultural Basin.
    Features: River channel, flooded inundated parcel, vibrant green vegetation fields.
    """
    w, h = 512, 512
    # Base terrain: warm vegetative / soil base
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Agricultural patch grid
    for y in range(0, h, 64):
        for x in range(0, w, 64):
            hue = np.random.randint(40, 110)
            img[y:y+64, x:x+64] = [hue, np.random.randint(140, 195), np.random.randint(40, 80)]
            
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    
    # Draw winding river / main water body
    river_points = [
        (40, 0), (90, 100), (140, 180), (220, 260), (320, 310), (410, 390), (480, 512)
    ]
    draw.line(river_points, fill=(28, 90, 160), width=45)
    
    # Draw flooded submerged basin
    draw.polygon([(180, 220), (280, 200), (360, 280), (290, 360), (190, 310)], fill=(32, 105, 175))
    
    # Add subtle texture noise
    pil_img = pil_img.filter(ImageFilter.GaussianBlur(1.2))
    out_path = OUTPUT_DIR / "flood_sentinel2_optical.png"
    pil_img.save(out_path)
    print(f"Generated Scenario 1: {out_path}")

def generate_scenario_2():
    """
    Scenario 2: Bi-Temporal Urban Expansion (Sentinel-2 Pair: T1 2022 and T2 2024).
    T1: Natural scrubland and agricultural parcel.
    T2: Replaced with large concrete industrial park and new asphalt bypass highway.
    """
    w, h = 512, 512
    
    # Base T1: Rural landscape
    t1_arr = np.zeros((h, w, 3), dtype=np.uint8)
    t1_arr[:, :] = [70, 145, 55]  # Green scrub
    
    t1_pil = Image.fromarray(t1_arr)
    d1 = ImageDraw.Draw(t1_pil)
    # Secondary rural dirt road
    d1.line([(0, 240), (512, 280)], fill=(160, 140, 110), width=8)
    # Small farm cluster
    d1.rectangle([(380, 80), (440, 140)], fill=(120, 150, 70))
    t1_pil = t1_pil.filter(ImageFilter.GaussianBlur(1.0))
    
    # Base T2: Same base, but with massive industrial development & paved bypass
    t2_pil = t1_pil.copy()
    d2 = ImageDraw.Draw(t2_pil)
    # New multi-lane highway
    d2.line([(0, 235), (512, 285)], fill=(65, 65, 75), width=22)
    # Highway lane markings
    d2.line([(0, 235), (512, 285)], fill=(220, 220, 220), width=2)
    
    # New concrete warehouse / industrial logistics center
    d2.rectangle([(120, 80), (310, 200)], fill=(215, 218, 222))  # Main concrete roof
    d2.rectangle([(140, 100), (220, 170)], fill=(175, 185, 195))  # High-reflectance section
    d2.rectangle([(230, 100), (290, 170)], fill=(190, 195, 205))
    
    # Paved parking & loading docks
    d2.rectangle([(110, 65), (320, 80)], fill=(90, 95, 100))
    
    t1_path = OUTPUT_DIR / "urban_t1_2022.png"
    t2_path = OUTPUT_DIR / "urban_t2_2024.png"
    t1_pil.save(t1_path)
    t2_pil.save(t2_path)
    print(f"Generated Scenario 2: {t1_path} and {t2_path}")

def generate_scenario_3():
    """
    Scenario 3: Cross-Modal Optical + SAR Pair (Simulated Cartosat-2S & RISAT / Sentinel-1).
    Optical: Heavy cumulus cloud cover obscuring an oil refinery and seaport.
    SAR: Penetrates clouds, showing bright corner-reflector returns on 6 oil tanks and dark water.
    """
    w, h = 512, 512
    
    # 1. Base terrain (ground truth underneath)
    under_arr = np.zeros((h, w, 3), dtype=np.uint8)
    under_arr[:, :260] = [80, 110, 75]  # Coastal land
    under_arr[:, 260:] = [25, 70, 130]  # Harbor water
    
    # Ground truth tanks
    tanks = [(80, 120), (160, 120), (80, 200), (160, 200), (80, 280), (160, 280)]
    
    # Optical with dense monsoon clouds
    opt_pil = Image.fromarray(under_arr.copy())
    d_opt = ImageDraw.Draw(opt_pil)
    # Clouds
    cloud_color = (245, 248, 252)
    d_opt.ellipse([(20, 40), (320, 360)], fill=cloud_color)
    d_opt.ellipse([(140, 150), (450, 480)], fill=cloud_color)
    opt_pil = opt_pil.filter(ImageFilter.GaussianBlur(18.0))
    
    # 2. SAR C-Band backscatter (Grayscale intensity)
    # Land has moderate speckled backscatter (~110)
    sar_arr = np.random.normal(loc=105, scale=18, size=(h, w)).clip(40, 210).astype(np.uint8)
    
    # Water has specular reflection -> very low backscatter (~25)
    sar_arr[:, 260:] = np.random.normal(loc=22, scale=8, size=(h, w - 260)).clip(5, 55).astype(np.uint8)
    
    sar_pil = Image.fromarray(sar_arr).convert("RGB")
    d_sar = ImageDraw.Draw(sar_pil)
    
    # Metal cylindrical storage tanks produce high double-bounce radar return (pure white > 245)
    for tx, ty in tanks:
        d_sar.ellipse([(tx - 18, ty - 18), (tx + 18, ty + 18)], fill=(255, 255, 255))
        
    opt_path = OUTPUT_DIR / "co_registered_optical_cloudy.png"
    sar_path = OUTPUT_DIR / "co_registered_sar_risat.png"
    opt_pil.save(opt_path)
    sar_pil.save(sar_path)
    print(f"Generated Scenario 3: {opt_path} and {sar_path}")

if __name__ == "__main__":
    generate_scenario_1()
    generate_scenario_2()
    generate_scenario_3()
    print("All sample remote sensing scenarios generated successfully.")
