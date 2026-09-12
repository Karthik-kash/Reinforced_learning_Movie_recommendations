# MovieVerse

MovieVerse is a full-stack movie discovery prototype. It combines a Python recommendation engine with a FastAPI API and a React application for authenticated, personalized movie browsing.

## Current product

- React, TypeScript, Vite, and Tailwind CSS frontend
- FastAPI backend with JWT-protected routes
- Registration, login, demo login, and first-use genre onboarding
- Search across the local movie catalog by title or genre
- Personalized recommendations, watchlist, history, ratings, dashboard, and profile views
- TF-IDF and cosine-similarity candidate generation
- Genre-level contextual-bandit/Q-value reranking from feedback
- Local CSV, JSON, and joblib persistence; no relational database

The active application is the React + FastAPI version. `app.py` is the older Streamlit interface and remains only as a compatibility path.

## Architecture at a glance

```text
React frontend (frontend-react)
        |
        | HTTP + Bearer JWT
        v
FastAPI API (backend/app)
        |
        +--> JSON auth store and user profiles
        +--> movie catalog and poster metadata
        +--> recommendation container
                 +--> preprocessing
                 +--> TF-IDF content recommender
                 +--> RL-style reranker
                 +--> feedback and profile services
```

At backend startup, the application loads `data/movies.csv`, rebuilds `data/processed_movies.csv`, loads `models/content_model.pkl` and `models/rl_agent.pkl`, and merges poster data from `data/poster_metadata.csv` when that file exists.

## Repository layout

```text
MovieVerse/
├── backend/app/              FastAPI application, routes, auth, services
├── frontend-react/           Active React + TypeScript client
├── src/                      Recommendation and profile domain logic
├── data/                     Movie catalog, processed data, poster metadata
├── models/                   Saved content and RL model artifacts
├── user_data/                Local users and interaction JSON files
├── scripts/                  Optional metadata enrichment utilities
├── app.py                    Legacy Streamlit entry point
├── requirements.txt          Python dependencies
└── .env.example              JWT configuration template
```

Important implementation files include:

- `backend/app/main.py`: creates FastAPI, configures CORS, initializes application state, and registers `/api` routes.
- `backend/app/infrastructure/container.py`: builds the recommendation container and loads catalog/model data.
- `backend/app/infrastructure/auth_store.py`: persists users in JSON and creates the demo user.
- `backend/app/services/catalog.py`: coordinates recommendations, search, profile, interactions, and dashboard data.
- `src/recommender.py`: generates content-based candidates.
- `src/rl_agent.py`: reranks candidates using learned genre values.
- `src/user_profile.py` and `src/feedback.py`: persist interaction state and apply rating feedback.
- `frontend-react/src/App.tsx`: auth gate, onboarding gate, navigation, page loading, and interaction actions.

## End-to-end behavior

1. A user registers, logs in, or chooses the demo account.
2. The backend returns a JWT. The frontend keeps it in `sessionStorage` and sends it as a Bearer token.
3. New accounts complete genre onboarding; preferences are stored in the user profile.
4. The recommendations route selects candidates by preferred genres or samples the catalog when no preferences exist.
5. Watched movies are excluded, then the RL-style agent reranks candidates using genre Q-values.
6. Search, watchlist, history, profile, and dashboard requests read the same local catalog and user state.
7. Ratings become reward signals and update the profile/learning state used by later recommendations.

## API surface

The backend is mounted under `/api` and is available in the FastAPI Swagger UI at `/docs`.

| Area | Endpoints | Auth |
| --- | --- | --- |
| Health | `GET /api/health` | Public |
| Auth | `POST /api/auth/register`, `/login`, `/demo`, `GET /me` | `/me` protected |
| Movies | `GET /api/movies/search`, `/{movie_id}`, `/{movie_id}/similar` | Public |
| Recommendations | `GET /api/recommendations` | Protected |
| Profile | `GET /api/profile`, `PUT /api/profile/preferences` | Protected |
| Interactions | History, watchlist, watched, rating, add/remove watchlist | Protected |
| Dashboard | `GET /api/dashboard` | Protected |

## Data and persistence

There is currently no SQL or NoSQL database. This is a local prototype with file-based persistence:

- `data/movies.csv`: source movie catalog.
- `data/processed_movies.csv`: generated feature data used by the recommender.
- `data/poster_metadata.csv`: optional TMDB poster metadata merged into API movie responses.
- `user_data/users.json`: account records, usernames, email addresses, and Argon2 password hashes. The demo account is ensured on backend startup.
- `user_data/interactions.json`: per-user preferred genres, watched movies, ratings, watchlist, and summary values.
- `models/content_model.pkl`: saved TF-IDF/content model artifact.
- `models/rl_agent.pkl`: saved RL-style agent state.

JSON storage is suitable for a local demo, but it is not designed for concurrent production traffic, migrations, backups, or multi-process deployments.

## Run locally

### Backend

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend defaults to `http://localhost:8000`. The frontend currently uses `http://localhost:8000/api` unless `VITE_API_URL` is provided.

### Frontend

In a second PowerShell terminal:

```powershell
cd frontend-react
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

To run the backend on another port, configure the frontend before starting Vite:

```powershell
$env:VITE_API_URL = "http://localhost:8001/api"
npm run dev
```

Useful frontend commands are `npm run build`, `npm run lint`, and `npm run preview`.

### Optional legacy interface

```powershell
streamlit run app.py
```

This path is separate from the active React client and is not required to run the current application.

## Configuration and metadata enrichment

Copy `.env.example` to `.env` and set a strong JWT secret for anything beyond local experimentation:

```powershell
copy .env.example .env
```

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=60
```

Poster enrichment is optional. The utility in `scripts/enrich_movie_metadata.py` uses TMDB and writes `data/poster_metadata.csv` plus an unmatched-title report. It is not called during normal API requests.

```powershell
$env:TMDB_API_KEY = "your-tmdb-api-key"
python scripts/enrich_movie_metadata.py
```

## Limitations and next steps

- Replace JSON persistence with a database and proper migrations.
- Move secrets and CORS origins into a production configuration system.
- Add refresh/revocation tokens, rate limiting, and deployment hardening.
- Improve recommendation evaluation and user-level model isolation.
- Resolve or provide fallback artwork for unmatched poster metadata.

MovieVerse is currently a learning and portfolio prototype, not a production deployment.
