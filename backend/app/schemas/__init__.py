from typing import Any

from pydantic import BaseModel, Field


class Movie(BaseModel):
    movie_id: int
    title: str
    genre: str = ""
    overview: str = ""
    vote: float = 0.0
    popularity: float = 0.0
    release_date: str = ""
    runtime: float = 0.0
    director: str = ""
    tagline: str = ""
    poster_url: str | None = None


class Recommendation(Movie):
    reason: str = "Suggested for you"
    predicted_score: float = 3.0


class Profile(BaseModel):
    user_id: str
    preferred_genres: list[str] = Field(default_factory=list)
    watched_movies: list[int] = Field(default_factory=list)
    rated_movies: dict[str, float] = Field(default_factory=dict)
    watchlist: list[int] = Field(default_factory=list)
    total_ratings: int = 0
    avg_rating: float = 0.0


class PreferencesUpdate(BaseModel):
    preferred_genres: list[str] = Field(default_factory=list)


class RatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)


class Dashboard(BaseModel):
    movies_watched: int
    movies_rated: int
    average_rating: float
    genre_preferences: list[dict[str, Any]]


class PaginatedMovies(BaseModel):
    items: list[Movie | Recommendation]
    page: int
    limit: int
    total: int
