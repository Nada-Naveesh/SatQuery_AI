import os
from typing import List, Tuple
from fastapi import UploadFile, HTTPException
from backend.app.config import settings

ALLOWED_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}

async def validate_upload_files(files: List[UploadFile]) -> List[Tuple[bytes, str]]:
    """
    Validates uploaded files for size, extension, and integrity.
    Returns list of (file_bytes, filename).
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one satellite image file is required.")

    if len(files) > 2:
        raise HTTPException(
            status_code=400,
            detail=f"Currently up to 2 images supported (single scene, temporal pair, or optical-SAR pair). Received: {len(files)}."
        )

    validated = []
    for f in files:
        ext = os.path.splitext(f.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' has unsupported extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        content = await f.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.MAX_IMAGE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' is {size_mb:.1f}MB, which exceeds the limit of {settings.MAX_IMAGE_SIZE_MB}MB."
            )

        validated.append((content, f.filename or "image.png"))

    return validated
