from fastapi import APIRouter, Depends, Request

from backend.app.auth.dependencies import get_current_user_id
from backend.app.schemas import Dashboard
from backend.app.services.catalog import get_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=Dashboard)
def dashboard(request: Request, user_id: str = Depends(get_current_user_id)):
    return get_dashboard(request.app.state.container, user_id)
