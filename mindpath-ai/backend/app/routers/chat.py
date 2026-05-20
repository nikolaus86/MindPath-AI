from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import ChatResponse, MessageCreate, MessageRead
from ..services.chat_service import ChatService
from ..mini_apps_catalog import MINI_APPS
from ..services.session_service import SessionService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{session_id}/messages", response_model=ChatResponse)
async def add_message(
    session_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    user_message, assistant_message, suggested_app = await ChatService.add_user_message(
        db, session, payload.text
    )
    suggested_title = (
        MINI_APPS[suggested_app]["title"] if suggested_app and suggested_app in MINI_APPS else None
    )
    return ChatResponse(
        user_message=user_message,
        assistant_message=assistant_message,
        suggested_app=suggested_app,
        suggested_app_title=suggested_title,
    )


@router.get("/{session_id}/messages", response_model=list[MessageRead])
async def list_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = await SessionService.get_owned_session(db, current_user, session_id)
    return await ChatService.list_messages(db, session)
