export type Page = 'Recommendations' | 'Search' | 'Watchlist' | 'History' | 'Dashboard' | 'Profile'

export type Movie = {
  movie_id: number
  title: string
  genre: string
  overview: string
  vote: number
  popularity: number
  release_date: string
  runtime: number
  director: string
  tagline: string
  poster_url: string | null
  reason?: string
  predicted_score?: number
}

export type Profile = {
  user_id: string
  preferred_genres: string[]
  watched_movies: number[]
  rated_movies: Record<string, number>
  watchlist: number[]
  total_ratings: number
  avg_rating: number
}

export type Dashboard = {
  movies_watched: number
  movies_rated: number
  average_rating: number
  genre_preferences: { genre: string; score: number }[]
}
