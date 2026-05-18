from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import ChatResponse, MessageCreate, MessageRead
from ..services.chat_service import ChatService
from ..services.session_service import SessionService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{session_id}/messages", response_model=ChatResponse)
def add_message(
    session_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    session = SessionService.get_owned_session(db, current_user, session_id)
    user_message, assistant_message = ChatService.add_user_message(db, session, payload.text)
    return ChatResponse(user_message=user_message, assistant_message=assistant_message)


@router.get("/{session_id}/messages", response_model=list[MessageRead])
def list_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    session = SessionService.get_owned_session(db, current_user, session_id)
    return ChatService.list_messages(db, session)
