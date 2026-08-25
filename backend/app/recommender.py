import pickle
from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import ARTIFACTS_DIR
from .tmdb import fetch_poster


def _build_feature_matrix(movies: pd.DataFrame):
    """Rebuild the movie feature matrix from the stored tags."""
    tags = movies["tags"].fillna("").astype(str)
    vectorizer = CountVectorizer(max_features=500, stop_words="english")
    return vectorizer.fit_transform(tags)


def _is_square_numeric_matrix(candidate: object, movie_count: int) -> bool:
    """Return True when the candidate looks like a valid similarity matrix."""
    if hasattr(candidate, "toarray") or hasattr(candidate, "tocsr"):
        return False

    try:
        values = np.asarray(candidate)
    except Exception:
        return False

    return (
        values.ndim == 2
        and values.shape == (movie_count, movie_count)
        and np.issubdtype(values.dtype, np.number)
    )


def _serialize_movie(movie: Any) -> dict[str, Any]:
    """Normalize movie rows to JSON-serializable dictionaries."""
    if hasattr(movie, "movie_id"):
        movie_id = movie.movie_id
    else:
        movie_id = movie["movie_id"]

    if hasattr(movie, "title"):
        title = movie.title
    else:
        title = movie["title"]

    return {"movie_id": int(movie_id), "title": str(title)}


def _resolve_movie_index(
    movies: pd.DataFrame,
    *,
    movie_id: int | None = None,
    movie_title: str | None = None,
) -> int:
    """Find the row index for the selected movie."""
    if movie_id is not None:
        matching_rows = movies.index[movies["movie_id"].astype(int) == int(movie_id)].tolist()
        label = f"movie_id={movie_id}"
    elif movie_title:
        matching_rows = movies.index[movies["title"].astype(str) == movie_title].tolist()
        label = f"title={movie_title}"
    else:
        raise ValueError("Provide a movie_id or a title.")

    if not matching_rows:
        raise ValueError(f"Movie not found: {label}")

    return matching_rows[0]


@lru_cache(maxsize=1)
def load_artifacts() -> tuple[pd.DataFrame, object]:
    """Load the trained movie data and a usable similarity structure once."""
    movie_list_path = ARTIFACTS_DIR / "movie_list.pkl"
    similarity_path = ARTIFACTS_DIR / "similarity.pkl"

    with movie_list_path.open("rb") as movie_file:
        movies = pickle.load(movie_file)

    similarity = None
    if similarity_path.exists():
        with similarity_path.open("rb") as similarity_file:
            similarity = pickle.load(similarity_file)

    if not isinstance(movies, pd.DataFrame):
        raise TypeError("movie_list.pkl must contain a pandas DataFrame.")

    if not _is_square_numeric_matrix(similarity, len(movies)):
        similarity = _build_feature_matrix(movies)
    else:
        similarity = np.asarray(similarity)

    return movies, similarity


def list_movies(movies: pd.DataFrame) -> list[dict[str, Any]]:
    """Return the movie catalogue in a frontend-friendly format."""
    return [_serialize_movie(movie) for movie in movies.itertuples(index=False)]


def recommend(
    movies: pd.DataFrame,
    similarity: object,
    *,
    movie_id: int | None = None,
    movie_title: str | None = None,
    limit: int = 5,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return the most similar movies and their poster URLs."""
    movie_index = _resolve_movie_index(
        movies,
        movie_id=movie_id,
        movie_title=movie_title,
    )

    if _is_square_numeric_matrix(similarity, len(movies)):
        similarity_scores = np.asarray(similarity[movie_index]).ravel()
    else:
        similarity_scores = cosine_similarity(similarity[movie_index], similarity).ravel()

    distances = sorted(enumerate(similarity_scores), reverse=True, key=lambda item: item[1])
    selected_movie = _serialize_movie(movies.iloc[movie_index])

    recommendations = []
    for index, _score in distances[1 : limit + 1]:
        selected = movies.iloc[index]
        recommendations.append(
            {
                **_serialize_movie(selected),
                "poster_url": fetch_poster(int(selected.movie_id)),
            }
        )

    return selected_movie, recommendations
