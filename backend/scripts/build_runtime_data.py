from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TOP_N = 20
BACKEND_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BACKEND_ROOT / "notebooks" / "artificats"
OUTPUT_DIR = BACKEND_ROOT / "data"
MOVIES_JSON = OUTPUT_DIR / "movies.json"
RECOMMENDATIONS_JSON = OUTPUT_DIR / "recommendations.json"


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
    movie_ids = [movie["movie_id"] for movie in normalized_movies]

    tags = movies["tags"].fillna("").astype(str)
    vectorizer = CountVectorizer(max_features=500, stop_words="english")
    similarity = vectorizer.fit_transform(tags)
    similarity_scores = cosine_similarity(similarity, similarity)
    np.fill_diagonal(similarity_scores, -1)

    recommendations: list[list[int]] = []
    for index, movie_id in enumerate(movie_ids):
        row = similarity_scores[index]
        top_indices = np.argpartition(row, -TOP_N)[-TOP_N:]
        top_indices = top_indices[np.argsort(row[top_indices])[::-1]]
        recommendations.append([int(movie_ids[i]) for i in top_indices])

    MOVIES_JSON.write_text(
        json.dumps(normalized_movies, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    RECOMMENDATIONS_JSON.write_text(
        json.dumps(recommendations, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(f"Wrote {MOVIES_JSON}")
    print(f"Wrote {RECOMMENDATIONS_JSON}")


if __name__ == "__main__":
    main()
