from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BACKEND_ROOT / "notebooks" / "artificats"
OUTPUT_DIR = BACKEND_ROOT / "data"
MOVIES_JSON = OUTPUT_DIR / "movies.json"
SIMILARITY_MATRIX_PATH = OUTPUT_DIR / "similarity.npy"


def _load_pickle(path: Path):
    with path.open("rb") as file_handle:
        return pickle.load(file_handle)


def main() -> None:
    movie_list_path = ARTIFACTS_DIR / "movie_list.pkl"

    movies = _load_pickle(movie_list_path)

    if not isinstance(movies, pd.DataFrame):
        raise TypeError("movie_list.pkl must contain a pandas DataFrame.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    normalized_movies = [
        {"movie_id": int(row.movie_id), "title": str(row.title)}
        for row in movies.itertuples(index=False)
    ]

    tags = movies["tags"].fillna("").astype(str)
    vectorizer = CountVectorizer(max_features=500, stop_words="english")
    feature_matrix = vectorizer.fit_transform(tags)
    similarity_scores = cosine_similarity(feature_matrix, feature_matrix).astype(np.float32)
    np.fill_diagonal(similarity_scores, -1.0)

    MOVIES_JSON.write_text(
        json.dumps(normalized_movies, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    np.save(SIMILARITY_MATRIX_PATH, similarity_scores)

    print(f"Wrote {MOVIES_JSON}")
    print(f"Wrote {SIMILARITY_MATRIX_PATH}")


if __name__ == "__main__":
    main()
