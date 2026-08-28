from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_cors_origins
from .recommender import list_movies, load_artifacts, recommend
from .schemas import HealthResponse, MovieCatalogResponse, RecommendationsResponse


app = FastAPI(title="Movie Recommendation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"message": "Movie Recommendation API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/movies", response_model=MovieCatalogResponse, tags=["movies"])
def get_movies() -> dict[str, list[dict[str, object]]]:
    movies, _movie_index_by_id, _title_to_movie_index, _similarity_matrix = load_artifacts()
    return {"movies": list_movies(movies)}


@app.get("/recommendations", response_model=RecommendationsResponse, tags=["movies"])
def get_recommendations(
    movie_id: int | None = Query(default=None),
    title: str | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
) -> dict[str, object]:
    if movie_id is None and not title:
        raise HTTPException(
            status_code=400,
            detail="Provide either movie_id or title.",
        )

    movies, movie_index_by_id, title_to_movie_index, similarity_matrix = load_artifacts()

    try:
        selected_movie, recommendations = recommend(
            movies,
            movie_index_by_id,
            title_to_movie_index,
            similarity_matrix,
            movie_id=movie_id,
            movie_title=title,
            limit=limit,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "selected_movie": selected_movie,
        "recommendations": recommendations,
    }
