from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class MovieOption(BaseModel):
    movie_id: int
    title: str


class RecommendationItem(MovieOption):
    poster_url: str | None = None


class MovieCatalogResponse(BaseModel):
    movies: list[MovieOption]


class RecommendationsResponse(BaseModel):
    selected_movie: MovieOption
    recommendations: list[RecommendationItem]
