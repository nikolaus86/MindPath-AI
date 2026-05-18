from sqlalchemy.orm import Session

from ..models import ContextFile, SessionModel
from .context_service import ContextService

APP_TITLES = {
    "problem-analysis": "Problem Analysis",
    "anxiety-helper": "Anxiety Helper",
    "decision-assistant": "Decision Assistant",
    "goal-planner": "Goal Planner",
}


class RouterService:
    @staticmethod
    def route_session(db: Session, session: SessionModel) -> tuple[str, str, ContextFile]:
        context = ContextService.get_latest_context(db, session)
        if context is None:
            context = ContextService.build_context(db, session)

        text = f"{context.problem} {context.emotion} {context.goal} {context.summary}".lower()
        app_id, reason = RouterService.detect_app(text)
        context.recommended_app = app_id
        db.add(context)
        db.commit()
        db.refresh(context)
        return app_id, reason, context

    @staticmethod
    def detect_app(text: str) -> tuple[str, str]:
        if any(word in text for word in ["anxiety", "worry", "stress", "panic", "afraid"]):
            return "anxiety-helper", "The session contains worry, stress, or panic keywords."
        if any(word in text for word in ["choose", "decision", "option", "unsure"]):
            return "decision-assistant", "The session looks like a choice between options."
        if any(word in text for word in ["goal", "plan", "improve", "habit"]):
            return "goal-planner", "The session contains planning or improvement keywords."
        return "problem-analysis", "The session needs basic problem structuring first."
