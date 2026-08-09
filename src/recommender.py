import pickle

import numpy as np
import pandas as pd
import streamlit as st
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


@st.cache_resource
def load_artifacts() -> tuple[pd.DataFrame, object]:
    """Load the trained movie data and a usable similarity structure once."""
    with (ARTIFACTS_DIR / "movie_list.pkl").open("rb") as movie_file:
        movies = pickle.load(movie_file)

    similarity_path = ARTIFACTS_DIR / "similarity.pkl"
    similarity = None
    if similarity_path.exists():
        with similarity_path.open("rb") as similarity_file:
            similarity = pickle.load(similarity_file)

    if not _is_square_numeric_matrix(similarity, len(movies)):
        similarity = _build_feature_matrix(movies)
    else:
        similarity = np.asarray(similarity)

    return movies, similarity


def recommend(
    movie: str,
    movies: pd.DataFrame,
    similarity: object,
    limit: int = 5,
) -> list[tuple[str, str | None]]:
    """Return the most similar movies and their poster URLs."""
    matching_rows = movies.index[movies["title"] == movie].tolist()
    if not matching_rows:
        raise ValueError(f"Movie not found: {movie}")

    movie_index = matching_rows[0]
    if _is_square_numeric_matrix(similarity, len(movies)):
        similarity_scores = np.asarray(similarity[movie_index])
    else:
        similarity_scores = cosine_similarity(similarity[movie_index], similarity).ravel()

    distances = sorted(enumerate(similarity_scores), reverse=True, key=lambda item: item[1])

    recommendations = []
    for index, _score in distances[1 : limit + 1]:
        selected = movies.iloc[index]
        recommendations.append(
            (selected.title, fetch_poster(int(selected.movie_id)))
        )

    return recommendations
