from fastapi import APIRouter, Depends, Query, Request

from backend.app.auth.dependencies import get_current_user_id
from backend.app.schemas import Recommendation
from backend.app.services.catalog import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[Recommendation])
def recommendations(request: Request, limit: int = Query(12, ge=1, le=50), user_id: str = Depends(get_current_user_id)):
    return get_recommendations(request.app.state.container, user_id, limit)
