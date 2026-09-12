from fastapi import APIRouter

from backend.app.api.routes import auth, dashboard, health, interactions, movies, profile, recommendations

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(movies.router)
api_router.include_router(recommendations.router)
api_router.include_router(profile.router)
api_router.include_router(interactions.router)
api_router.include_router(dashboard.router)
