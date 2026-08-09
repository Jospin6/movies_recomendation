import pickle

import pandas as pd
import streamlit as st

from .config import ARTIFACTS_DIR
from .tmdb import fetch_poster


@st.cache_resource
def load_artifacts() -> tuple[pd.DataFrame, object]:
    """Load the trained movie data and similarity matrix once."""
    with (ARTIFACTS_DIR / "movie_list.pkl").open("rb") as movie_file:
        movies = pickle.load(movie_file)

    with (ARTIFACTS_DIR / "similarity.pkl").open("rb") as similarity_file:
        similarity = pickle.load(similarity_file)

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
    distances = sorted(
        enumerate(similarity[movie_index]),
        reverse=True,
        key=lambda item: item[1],
    )

    recommendations = []
    for index, _score in distances[1 : limit + 1]:
        selected = movies.iloc[index]
        recommendations.append(
            (selected.title, fetch_poster(int(selected.movie_id)))
        )

    return recommendations
