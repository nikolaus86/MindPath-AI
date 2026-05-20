from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import SummaryResponse
from ..services.session_service import SessionService
from ..services.summary_service import SummaryService

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/{session_id}", response_model=SummaryResponse)
async def get_summary(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    return await SummaryService.build_summary(db, current_user, session)
