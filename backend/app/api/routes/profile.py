from fastapi import APIRouter, Depends, Request

from backend.app.auth.dependencies import get_current_user_id
from backend.app.schemas import PreferencesUpdate, Profile
from backend.app.services.catalog import get_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=Profile)
def profile(request: Request, user_id: str = Depends(get_current_user_id)):
    return get_profile(request.app.state.container, user_id)


@router.put("/preferences", response_model=Profile)
def update_preferences(request: Request, payload: PreferencesUpdate, user_id: str = Depends(get_current_user_id)):
    container = request.app.state.container
    profile = get_profile(container, user_id)
    profile["preferred_genres"] = payload.preferred_genres
    container.profiles.save_all_users()
    return profile
