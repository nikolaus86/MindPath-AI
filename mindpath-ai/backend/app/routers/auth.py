from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import TokenResponse, UserCreate, UserLogin, UserRead
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    payload: UserCreate, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    result = await AuthService.register(db, payload.email, payload.password)
    return TokenResponse(access_token=result.access_token, user=result.user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await AuthService.login(db, payload.email, payload.password)
    return TokenResponse(access_token=result.access_token, user=result.user)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
