from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SessionModel, User
from .chat_service import ChatService
from .context_service import ContextService
from .mini_app_service import MiniAppService
from .progress_service import ProgressService


class SummaryService:
    @staticmethod
    async def build_summary(db: AsyncSession, user: User, session: SessionModel) -> dict:
        messages = await ChatService.list_messages(db, session)
        context = await ContextService.get_latest_context(db, session)
        results = await MiniAppService.list_results(db, session)
        progress_entries = [
            entry
            for entry in await ProgressService.list_entries(db, user)
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
