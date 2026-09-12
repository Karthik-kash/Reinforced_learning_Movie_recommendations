from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.app.auth.dependencies import get_current_user_id
from backend.app.auth.password import verify_password
from backend.app.auth.tokens import create_access_token
from backend.app.infrastructure.auth_store import JsonAuthStore
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def get_store(request: Request) -> JsonAuthStore:
    return request.app.state.auth_store


def to_user_response(user: dict) -> UserResponse:
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        username=user["username"],
        is_demo=user.get("is_demo", False),
    )


def token_response(user: dict) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user["user_id"]), user=to_user_response(user))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request):
    store = get_store(request)
    if store.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = store.create_user(payload.email, payload.username, payload.password)
    request.app.state.container.profiles.create_profile(user["user_id"])
    return token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request):
    store = get_store(request)
    user = store.get_by_email(payload.email)
    if not user or user.get("is_demo") or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return token_response(user)


@router.post("/demo", response_model=TokenResponse)
def demo_login(request: Request):
    user = get_store(request).get_by_id("guest_user")
    if not user:
        raise HTTPException(status_code=503, detail="Demo profile is unavailable")
    return token_response(user)


@router.get("/me", response_model=UserResponse)
def me(user_id: str = Depends(get_current_user_id), store: JsonAuthStore = Depends(get_store)):
    user = store.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return to_user_response(user)
