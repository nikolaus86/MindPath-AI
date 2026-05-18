from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import MiniAppAnswer, MiniAppDefinition, MiniAppResultRead, MiniAppStart
from ..services.mini_app_service import MiniAppService
from ..services.session_service import SessionService

router = APIRouter(prefix="/mini-apps", tags=["mini-apps"])


@router.get("", response_model=list[MiniAppDefinition])
def list_mini_apps() -> object:
    return MiniAppService.list_apps()


@router.post("/{app_id}/start", response_model=MiniAppDefinition)
def start_mini_app(
    app_id: str,
    payload: MiniAppStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    SessionService.get_owned_session(db, current_user, payload.session_id)
    return MiniAppService.get_app(app_id)


@router.post("/{app_id}/answer", response_model=MiniAppResultRead)
def answer_mini_app(
    app_id: str,
    payload: MiniAppAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = SessionService.get_owned_session(db, current_user, payload.session_id)
    return MiniAppService.save_answers(db, session, app_id, payload.answers)


@router.get("/{session_id}/results", response_model=list[MiniAppResultRead])
def list_results(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = SessionService.get_owned_session(db, current_user, session_id)
    return MiniAppService.list_results(db, session)
