from typing import Any

import pandas as pd

from backend.app.infrastructure.container import AppContainer


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return ""
    if hasattr(value, "item"):
        return value.item()
    return value


def movie_from_row(row: pd.Series) -> dict[str, Any]:
    return {
        "movie_id": int(row["Movie_ID"]),
        "title": str(_clean_value(row.get("Movie_Title", ""))),
        "genre": str(_clean_value(row.get("Movie_Genre", ""))),
        "overview": str(_clean_value(row.get("Movie_Overview", ""))),
        "vote": float(_clean_value(row.get("Movie_Vote", 0)) or 0),
        "popularity": float(_clean_value(row.get("Movie_Popularity", 0)) or 0),
        "release_date": str(_clean_value(row.get("Movie_Release_Date", ""))),
        "runtime": float(_clean_value(row.get("Movie_Runtime", 0)) or 0),
        "director": str(_clean_value(row.get("Movie_Director", ""))),
        "tagline": str(_clean_value(row.get("Movie_Tagline", ""))),
        "poster_url": str(_clean_value(row.get("poster_url", ""))) or None,
    }


def get_profile(container: AppContainer, user_id: str) -> dict[str, Any]:
    profile = container.profiles.get_profile(user_id)
    return profile or container.profiles.create_profile(user_id)


def get_recommendations(container: AppContainer, user_id: str, limit: int) -> list[dict[str, Any]]:
    profile = get_profile(container, user_id)
    if profile.get("preferred_genres"):
        candidates = container.recommender.get_candidates_by_genre(
            profile["preferred_genres"], top_n=max(limit * 5, 40)
        )
    else:
        candidates = container.dataframe.sample(n=min(max(limit * 5, 40), len(container.dataframe)))

    candidates = candidates[~candidates["Movie_ID"].isin(profile.get("watched_movies", []))]
    ranked, reasons = container.rl_agent.get_reranked_list(candidates, profile)
    results = []
    for index, (_, row) in enumerate(ranked.head(limit).iterrows()):
        movie = movie_from_row(row)
        genres = str(row.get("Movie_Genre", "")).split(",")
        q_values = [container.rl_agent.q_table.get(genre.strip(), 0.0) for genre in genres]
        movie["reason"] = reasons[index] if index < len(reasons) else "Suggested for you"
        movie["predicted_score"] = round(3.0 + (sum(q_values) / len(q_values) * 2 if q_values else 0), 2)
        results.append(movie)
    return results


def search_movies(container: AppContainer, query: str, page: int, limit: int) -> dict[str, Any]:
    query = query.strip()
    frame = container.dataframe
    if query:
        title_matches = frame[frame["Movie_Title"].str.contains(query, case=False, na=False)]
        genre_matches = frame[frame["Movie_Genre"].str.contains(query, case=False, na=False)]
        frame = pd.concat([title_matches, genre_matches]).drop_duplicates(subset="Movie_ID")
    total = len(frame)
    start = max(page - 1, 0) * limit
    rows = [movie_from_row(row) for _, row in frame.iloc[start:start + limit].iterrows()]
    return {"items": rows, "page": page, "limit": limit, "total": total}


def movies_by_ids(container: AppContainer, movie_ids: list[int]) -> list[dict[str, Any]]:
    frame = container.dataframe[container.dataframe["Movie_ID"].isin(movie_ids)]
    by_id = {int(row["Movie_ID"]): movie_from_row(row) for _, row in frame.iterrows()}
    return [by_id[movie_id] for movie_id in movie_ids if movie_id in by_id]


def get_dashboard(container: AppContainer, user_id: str) -> dict[str, Any]:
    profile = get_profile(container, user_id)
    preferences = [
        {"genre": genre, "score": round(float(container.rl_agent.q_table.get(genre, 0.0)), 3)}
        for genre in profile.get("preferred_genres", [])
    ]
    return {
        "movies_watched": len(profile.get("watched_movies", [])),
        "movies_rated": profile.get("total_ratings", 0),
        "average_rating": round(float(profile.get("avg_rating", 0.0)), 2),
        "genre_preferences": preferences,
    }
