import os
from pathlib import Path

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data"
DEMO_SCENARIOS_DIR = DATA_DIR / "demo_scenarios"
STATIC_DIR = BASE_DIR / "static"
OVERLAYS_DIR = STATIC_DIR / "overlays"
REPORTS_DIR = STATIC_DIR / "reports"
SAMPLES_DIR = STATIC_DIR / "samples"
THUMBS_DIR = STATIC_DIR / "thumbs"

# Ensure runtime directories exist
for folder in [DATA_DIR, DEMO_SCENARIOS_DIR, STATIC_DIR, OVERLAYS_DIR, REPORTS_DIR, SAMPLES_DIR, THUMBS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "SatQuery AI"
    VERSION: str = "1.0.0"
    SIH_PS_ID: str = "26167"
    THEME: str = "Space Technology"
    ORGANIZATION: str = "ISRO / Department of Space"
    
    # Environment & Device
    DEVICE: str = "cuda" if os.environ.get("USE_CUDA", "0") == "1" else "cpu"
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() == "true"
    
    # Image constraints
    MAX_IMAGE_SIZE_MB: int = 50
    MAX_DIMENSION: int = 2048
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.50
    
    # Static paths
    BASE_DIR: Path = BASE_DIR
    ROOT_DIR: Path = BASE_DIR.parent
    DATA_DIR: Path = DATA_DIR
    DEMO_SCENARIOS_DIR: Path = DEMO_SCENARIOS_DIR
    STATIC_DIR: Path = STATIC_DIR
    OVERLAYS_DIR: Path = OVERLAYS_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    SAMPLES_DIR: Path = SAMPLES_DIR
    THUMBS_DIR: Path = THUMBS_DIR

settings = Settings()
