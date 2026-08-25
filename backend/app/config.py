import os
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BACKEND_ROOT / "notebooks" / "artificats"

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
TMDB_API_URL = (os.getenv("TMDB_API_URL", "") or "https://api.themoviedb.org/3").rstrip("/")
TMDB_IMAGE_BASE_URL = (
    os.getenv("TMDB_IMAGE_BASE_URL", "") or "https://image.tmdb.org/t/p/w500"
).rstrip("/")

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("BACKEND_CORS_ORIGINS", "").strip()
    if not raw_origins:
        return DEFAULT_CORS_ORIGINS.copy()

    origins = [origin.strip() for origin in raw_origins.split(",")]
    return [origin for origin in origins if origin] or DEFAULT_CORS_ORIGINS.copy()
