import json
from functools import lru_cache
from typing import Any

import numpy as np

from .config import MOVIE_CATALOG_PATH, SIMILARITY_MATRIX_PATH
from .tmdb import fetch_poster


def _load_json(path) -> Any:
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def _normalize_movie(movie: dict[str, Any]) -> dict[str, Any]:
    return {"movie_id": int(movie["movie_id"]), "title": str(movie["title"])}


def _resolve_movie_index(
    movie_index_by_id: dict[int, int],
    title_to_movie_index: dict[str, int],
    *,
    movie_id: int | None = None,
    movie_title: str | None = None,
) -> int:
    if movie_id is not None:
        resolved_movie_id = int(movie_id)
        resolved_movie_index = movie_index_by_id.get(resolved_movie_id)
        if resolved_movie_index is None:
            raise ValueError(f"Movie not found: movie_id={movie_id}")
        return resolved_movie_index

    if movie_title:
        resolved_movie_index = title_to_movie_index.get(movie_title)
        if resolved_movie_index is None:
            raise ValueError(f"Movie not found: title={movie_title}")
        return resolved_movie_index

    raise ValueError("Provide a movie_id or a title.")


@lru_cache(maxsize=1)
def load_artifacts() -> tuple[
    list[dict[str, Any]],
    dict[int, int],
    dict[str, int],
    np.ndarray,
]:
    """Load the precomputed movie catalog and similarity matrix once."""
    raw_movies = _load_json(MOVIE_CATALOG_PATH)
    similarity_matrix = np.load(SIMILARITY_MATRIX_PATH, mmap_mode="r", allow_pickle=False)

    if not isinstance(raw_movies, list):
        raise TypeError("movies.json must contain a list of movies.")

    movies: list[dict[str, Any]] = []
    movie_index_by_id: dict[int, int] = {}
    title_to_movie_index: dict[str, int] = {}

    for index, raw_movie in enumerate(raw_movies):
        if not isinstance(raw_movie, dict):
            raise TypeError("Each movie must be a JSON object.")

        movie = _normalize_movie(raw_movie)
        movies.append(movie)
        movie_index_by_id.setdefault(movie["movie_id"], index)
        title_to_movie_index.setdefault(movie["title"], index)

    if similarity_matrix.shape != (len(movies), len(movies)):
        raise ValueError("similarity.npy must be a square matrix aligned with movies.json.")

    return movies, movie_index_by_id, title_to_movie_index, similarity_matrix


def list_movies(movies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the movie catalogue in a frontend-friendly format."""
    return movies


def recommend(
    movies: list[dict[str, Any]],
    movie_index_by_id: dict[int, int],
    title_to_movie_index: dict[str, int],
    similarity_matrix: np.ndarray,
    *,
    movie_id: int | None = None,
    movie_title: str | None = None,
    limit: int = 5,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return the most similar movies and their poster URLs."""
    selected_movie_index = _resolve_movie_index(
        movie_index_by_id,
        title_to_movie_index,
        movie_id=movie_id,
        movie_title=movie_title,
    )

    similarity_scores = np.asarray(similarity_matrix[selected_movie_index], dtype=np.float32)
    ranked_indices = np.argsort(similarity_scores)[::-1]

    selected_movie = movies[selected_movie_index]
    recommendations = []
    for recommended_movie_index in ranked_indices:
        if recommended_movie_index == selected_movie_index:
            continue

        recommended_movie = movies[int(recommended_movie_index)]
        recommendations.append(
            {
                **recommended_movie,
                "poster_url": fetch_poster(int(recommended_movie["movie_id"])),
            }
        )

        if len(recommendations) >= limit:
            break

    return selected_movie, recommendations
