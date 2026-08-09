import requests

from .config import TMDB_API_KEY, TMDB_API_URL, TMDB_IMAGE_BASE_URL


def fetch_poster(movie_id: int) -> str | None:
    """Return the TMDB poster URL for a movie, when available."""
    if not TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY is missing. Add it to the .env file.")

    response = requests.get(
        f"{TMDB_API_URL}/movie/{movie_id}",
        params={"api_key": TMDB_API_KEY, "language": "en-US"},
        timeout=10,
    )
    response.raise_for_status()

    poster_path = response.json().get("poster_path")
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
