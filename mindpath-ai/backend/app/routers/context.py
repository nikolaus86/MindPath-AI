from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import ContextRead
from ..services.context_service import ContextService
from ..services.session_service import SessionService

router = APIRouter(prefix="/context", tags=["context"])


@router.post("/{session_id}/build", response_model=ContextRead)
async def build_context(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    return await ContextService.build_context(db, session)


@router.get("/{session_id}", response_model=ContextRead)
async def get_context(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    context = await ContextService.get_latest_context(db, session)
    if context is None:
        raise HTTPException(status_code=404, detail="Context is not built yet")
    return context
