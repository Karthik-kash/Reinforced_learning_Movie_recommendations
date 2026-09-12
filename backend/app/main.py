from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.core.config import FRONTEND_ORIGIN, USERS_PATH
from backend.app.infrastructure.auth_store import JsonAuthStore
from backend.app.infrastructure.container import build_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.auth_store = JsonAuthStore(USERS_PATH)
    app.state.container = build_container()
    yield


app = FastAPI(title="MovieVerse API", description="Movie recommendations and personalization API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "MovieVerse API", "status": "running"}
