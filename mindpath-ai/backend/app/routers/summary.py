from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import SummaryResponse
from ..services.session_service import SessionService
from ..services.summary_service import SummaryService

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/{session_id}", response_model=SummaryResponse)
def get_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    session = SessionService.get_owned_session(db, current_user, session_id)
    return SummaryService.build_summary(db, current_user, session)
