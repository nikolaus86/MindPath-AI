from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ContextFile, SessionModel
from .context_service import ContextService
from .llm_service import LlmService

APP_TITLES = {
    "problem-analysis": "Problem Analysis",
    "anxiety-helper": "Anxiety Helper",
    "decision-assistant": "Decision Assistant",
    "goal-planner": "Goal Planner",
}


class RouterService:
    @staticmethod
    async def route_session(
        db: AsyncSession, session: SessionModel
    ) -> tuple[str, str, ContextFile]:
        context = await ContextService.get_latest_context(db, session)
        if context is None:
            context = await ContextService.build_context(db, session)

        context_text = (
            f"Title: {session.title}\n"
            f"Problem: {context.problem}\n"
            f"Emotion: {context.emotion}\n"
            f"Goal: {context.goal}\n"
            f"Constraints: {context.constraints}\n"
            f"Summary: {context.summary}"
        )
        app_id, reason, _used_llm = await LlmService.route_session(context_text)
        context.recommended_app = app_id
        db.add(context)
        await db.commit()
        await db.refresh(context)
        return app_id, reason, context
