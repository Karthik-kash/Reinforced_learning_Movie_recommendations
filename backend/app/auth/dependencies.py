from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.auth.tokens import decode_access_token
from backend.app.infrastructure.auth_store import JsonAuthStore

bearer = HTTPBearer(auto_error=False)


def get_auth_store(request: Request) -> JsonAuthStore:
    return request.app.state.auth_store


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    auth_store: JsonAuthStore = Depends(get_auth_store),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None or auth_store.get_by_id(user_id) is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user_id
