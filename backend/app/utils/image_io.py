import io
import base64
from pathlib import Path
from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def load_image_from_bytes(file_bytes: bytes, filename: str = "") -> Tuple[np.ndarray, str]:
    """
    Loads an image from raw bytes into an RGB numpy uint8 array.
    Returns (image_array, format_str).
    Supports GeoTIFF / TIFF (including 16-bit multispectral / float), PNG, JPEG.
    """
    try:
        # Check if TIFF and try tifffile first if available
        is_tiff = filename.lower().endswith(('.tif', '.tiff')) or file_bytes[:4] in (b'II*\x00', b'MM\x00*')
        if is_tiff:
            try:
                import tifffile
                arr = tifffile.imread(io.BytesIO(file_bytes))
                is_sar_img = any(k in filename.lower() for k in ["sar", "s1", "risat"])
                if arr.ndim == 2:
                    if arr.dtype != np.uint8 or is_sar_img:
                        arr = normalize_remote_sensing_bands(arr, is_sar=is_sar_img)
                elif arr.ndim >= 3:
                    if arr.shape[0] in (1, 2, 3, 4, 12) and arr.shape[0] < arr.shape[1]:
                        # Channel-first format (C, H, W) -> (H, W, C)
                        arr = np.transpose(arr, (1, 2, 0))
                    if arr.dtype != np.uint8 or is_sar_img:
                        arr = normalize_remote_sensing_bands(arr, is_sar=is_sar_img)
                return arr, "TIFF"
            except Exception:
                pass  # Fall back to PIL

        pil_img = Image.open(io.BytesIO(file_bytes))
        fmt = pil_img.format or "PNG"
        
        # Convert to RGB if needed
        if pil_img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", pil_img.size, (255, 255, 255))
            background.paste(pil_img, mask=pil_img.split()[-1])
            pil_img = background
        elif pil_img.mode == "I;16" or pil_img.mode == "I":
            raw_arr = np.array(pil_img, dtype=np.float32)
            arr = normalize_remote_sensing_bands(raw_arr)
            return arr, fmt
        elif pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
            
        arr = np.array(pil_img, dtype=np.uint8)
        return arr, fmt
    except Exception as e:
        raise ValueError(f"Failed to decode image bytes: {str(e)}")

def load_image_from_path(file_path: Union[str, Path]) -> Tuple[np.ndarray, str]:
    """
    Loads an image from a filesystem path into an RGB numpy uint8 array.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Satellite image file not found: {path}")
    with open(path, "rb") as f:
        content = f.read()
    return load_image_from_bytes(content, filename=path.name)

def normalize_remote_sensing_bands(arr: np.ndarray, is_sar: bool = False) -> np.ndarray:
    """
    Normalizes remote sensing bands using robust percentile stretching (2% to 98%).
    If SAR, converts amplitude to decibels first.
    """
    arr_float = arr.astype(np.float32)
    
    if is_sar:
        # Convert SAR amplitude to dB scale
        arr_float = np.clip(arr_float, 1e-5, None)
        arr_float = 10.0 * np.log10(arr_float ** 2)
        
    # Percentile stretch per channel
    normalized = np.zeros_like(arr_float, dtype=np.uint8)
    if arr.ndim == 2:
        channels = [arr_float]
    else:
        channels = [arr_float[:, :, c] for c in range(arr_float.shape[2])]
        
    out_channels = []
    for ch in channels:
        p2, p98 = np.percentile(ch, (2, 98))
        if p98 > p2:
            stretched = np.clip((ch - p2) / (p98 - p2) * 255.0, 0, 255)
        else:
            stretched = np.zeros_like(ch)
        out_channels.append(stretched.astype(np.uint8))
        
    if len(out_channels) == 1:
        return np.repeat(out_channels[0][:, :, np.newaxis], 3, axis=2)
    elif len(out_channels) >= 3:
        return np.stack(out_channels[:3], axis=2)
    else:
        return np.stack([out_channels[0], out_channels[1], out_channels[0]], axis=2)

def numpy_to_base64(arr: np.ndarray, format: str = "PNG") -> str:
    """Encodes a uint8 numpy image array to a base64 data URI string."""
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    pil_img = Image.fromarray(arr)
    buffer = io.BytesIO()
    pil_img.save(buffer, format=format)
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{b64_str}"

def create_color_mask_overlay(
    base_image: np.ndarray,
    mask: np.ndarray,
    color_rgb: Tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.5
) -> np.ndarray:
    """
    Blends a binary/intensity mask (0 to 1 or 0 to 255) as a semi-transparent color overlay
    on top of the base image.
    """
    h, w = base_image.shape[:2]
    # Ensure mask is 2D and float [0, 1]
    if mask.ndim == 3:
        mask = mask.mean(axis=2)
    if mask.max() > 1.0:
        mask = mask.astype(np.float32) / 255.0
        
    # Resize mask if shape differs
    if mask.shape[:2] != (h, w):
        pil_mask = Image.fromarray((mask * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)
        mask = np.array(pil_mask, dtype=np.float32) / 255.0
        
    colored_layer = np.zeros((h, w, 3), dtype=np.float32)
    for c in range(3):
        colored_layer[:, :, c] = color_rgb[c]
        
    base_float = base_image.astype(np.float32)
    mask_weight = (mask[:, :, np.newaxis] * alpha)
    blended = base_float * (1.0 - mask_weight) + colored_layer * mask_weight
    return np.clip(blended, 0, 255).astype(np.uint8)

def draw_boxes_on_image(
    image: np.ndarray,
    boxes: list,
    color_rgb: Tuple[int, int, int] = (0, 255, 128),
    thickness: int = 3
) -> np.ndarray:
    """Draws bounding boxes and labels onto an image array."""
    pil_img = Image.fromarray(image.copy())
    draw = ImageDraw.Draw(pil_img)
    
    for box in boxes:
        xmin = getattr(box, 'xmin', box.get('xmin', 0))
        ymin = getattr(box, 'ymin', box.get('ymin', 0))
        xmax = getattr(box, 'xmax', box.get('xmax', 0))
        ymax = getattr(box, 'ymax', box.get('ymax', 0))
        label = getattr(box, 'label', box.get('label', 'Detection'))
        score = getattr(box, 'score', box.get('score', 1.0))
        
        # Draw rectangle
        for i in range(thickness):
            draw.rectangle([xmin - i, ymin - i, xmax + i, ymax + i], outline=color_rgb)
            
        # Draw label background
        text = f"{label} ({score:.0%})"
        draw.rectangle([xmin, max(0, ymin - 20), xmin + len(text) * 8 + 8, ymin], fill=color_rgb)
        draw.text((xmin + 4, max(0, ymin - 18)), text, fill=(0, 0, 0))
        
    return np.array(pil_img)
