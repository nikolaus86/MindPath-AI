from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import (
    MiniAppAnswer,
    MiniAppDefinition,
    MiniAppInsightResponse,
    MiniAppResultRead,
    MiniAppStart,
)
from ..services.mini_app_service import MiniAppService
from ..services.session_service import SessionService

router = APIRouter(prefix="/mini-apps", tags=["mini-apps"])


@router.get("", response_model=list[MiniAppDefinition])
def list_mini_apps() -> object:
    return MiniAppService.list_apps()


@router.post("/{app_id}/start", response_model=MiniAppDefinition)
async def start_mini_app(
    app_id: str,
    payload: MiniAppStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    await SessionService.get_owned_session(db, current_user, payload.session_id)
    return MiniAppService.get_app(app_id)


@router.post("/{app_id}/insight", response_model=MiniAppInsightResponse)
async def mini_app_insight(
    app_id: str,
    payload: MiniAppAnswer,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MiniAppInsightResponse:
    session = await SessionService.get_owned_session(db, current_user, payload.session_id)
    insight, llm_used = await MiniAppService.request_insight(
        db, session, app_id, payload.answers
    )
    return MiniAppInsightResponse(insight=insight, llm_used=llm_used)


@router.post("/{app_id}/answer", response_model=MiniAppResultRead)
async def answer_mini_app(
    app_id: str,
    payload: MiniAppAnswer,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = await SessionService.get_owned_session(db, current_user, payload.session_id)
    return await MiniAppService.save_answers(db, session, app_id, payload.answers)


@router.get("/{session_id}/results", response_model=list[MiniAppResultRead])
async def list_results(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    return await MiniAppService.list_results(db, session)
