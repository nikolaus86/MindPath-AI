from sqlalchemy.orm import Session

from ..models import SessionModel, User
from .chat_service import ChatService
from .context_service import ContextService
from .mini_app_service import MiniAppService
from .progress_service import ProgressService


class SummaryService:
    @staticmethod
    def build_summary(db: Session, user: User, session: SessionModel) -> dict:
        messages = ChatService.list_messages(db, session)
        context = ContextService.get_latest_context(db, session)
        results = MiniAppService.list_results(db, session)
        progress_entries = [
            entry
            for entry in ProgressService.list_entries(db, user)
            if entry.session_id == session.id
        ]
        return {
            "session": session,
            "context": context,
            "messages": messages,
            "mini_app_results": results,
            "latest_result": results[0] if results else None,
            "progress_entries": progress_entries,
        }
