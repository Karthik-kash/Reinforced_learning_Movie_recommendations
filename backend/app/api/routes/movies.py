from fastapi import APIRouter, Query, Request

from backend.app.schemas import Movie, PaginatedMovies
from backend.app.services.catalog import movie_from_row, search_movies

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/search", response_model=PaginatedMovies)
def search(request: Request, q: str = "", page: int = Query(1, ge=1), limit: int = Query(12, ge=1, le=50)):
    return search_movies(request.app.state.container, q, page, limit)


@router.get("/{movie_id}", response_model=Movie)
def get_movie(request: Request, movie_id: int):
    container = request.app.state.container
    matches = container.dataframe[container.dataframe["Movie_ID"] == movie_id]
    if matches.empty:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie_from_row(matches.iloc[0])


@router.get("/{movie_id}/similar", response_model=list[Movie])
def similar(request: Request, movie_id: int, limit: int = Query(10, ge=1, le=50)):
    container = request.app.state.container
    return [movie_from_row(row) for _, row in container.recommender.get_similar_movies(movie_id, limit).iterrows()]
