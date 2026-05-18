from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import SessionCreate, SessionRead
from ..services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    return SessionService.create_session(db, current_user, payload.title)


@router.get("", response_model=list[SessionRead])
def list_sessions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> object:
    return SessionService.list_sessions(db, current_user)


@router.get("/{session_id}", response_model=SessionRead)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    return SessionService.get_owned_session(db, current_user, session_id)


@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    SessionService.delete_session(db, current_user, session_id)
    return {"status": "deleted"}
