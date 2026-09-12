from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
MODEL_DIR = ROOT_DIR / "models"
USER_DATA_DIR = ROOT_DIR / "user_data"

MOVIES_PATH = DATA_DIR / "movies.csv"
PROCESSED_MOVIES_PATH = DATA_DIR / "processed_movies.csv"
POSTER_METADATA_PATH = DATA_DIR / "poster_metadata.csv"
CONTENT_MODEL_PATH = MODEL_DIR / "content_model.pkl"
RL_MODEL_PATH = MODEL_DIR / "rl_agent.pkl"
INTERACTIONS_PATH = USER_DATA_DIR / "interactions.json"
USERS_PATH = USER_DATA_DIR / "users.json"

FRONTEND_ORIGIN = "http://localhost:5173"
DEMO_USER_ID = "guest_user"
