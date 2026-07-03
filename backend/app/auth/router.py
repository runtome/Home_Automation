from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.session import get_db
from app.repositories.log_repository import LogRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenPair
from app.schemas.common import Message
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthError, AuthService
from app.services.log_service import LogService
from app.utils.rate_limit import limiter

router = APIRouter()
settings = get_settings()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=UserRepository(db),
        refresh_repo=RefreshTokenRepository(db),
        log_service=LogService(LogRepository(db)),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    try:
        user = await service.register_user(data)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await db.commit()
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
@limiter.limit(settings.login_rate_limit)
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        tokens = await service.login(data.username, data.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    await db.commit()
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        tokens = await service.refresh(data.refresh_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    await db.commit()
    return tokens


@router.post("/logout", response_model=Message)
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> Message:
    try:
        await service.logout(data.refresh_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    await db.commit()
    return Message(detail="logged out")
