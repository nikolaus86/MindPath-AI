from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import ProgressCreate, ProgressList, ProgressRead
from ..services.progress_service import ProgressService
from ..services.session_service import SessionService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("", response_model=ProgressRead)
async def create_progress(
    payload: ProgressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    if payload.session_id is not None:
        await SessionService.get_owned_session(db, current_user, payload.session_id)
    return await ProgressService.create_entry(
        db,
        current_user,
        payload.mood_score,
        payload.note,
        payload.session_id,
    )


@router.get("", response_model=ProgressList)
async def list_progress(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ProgressList:
    entries = await ProgressService.list_entries(db, current_user)
    return ProgressList(entries=entries, average_mood=ProgressService.average_mood(entries))
