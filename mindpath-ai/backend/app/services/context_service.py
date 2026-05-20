from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ContextFile, Message, SessionModel
from .llm_service import GeminiService


class ContextService:
    @staticmethod
    async def get_latest_context(
        db: AsyncSession, session: SessionModel
    ) -> ContextFile | None:
        return await db.scalar(
            select(ContextFile)
            .where(ContextFile.session_id == session.id)
            .order_by(ContextFile.created_at.desc())
        )

    @staticmethod
    async def build_context(db: AsyncSession, session: SessionModel) -> ContextFile:
        result = await db.scalars(
            select(Message)
            .where(Message.session_id == session.id, Message.role == "user")
            .order_by(Message.created_at.asc())
        )
        messages = list(result.all())
        user_texts = [message.text for message in messages]
        combined = " ".join(user_texts).strip()
        latest_text = user_texts[-1] if user_texts else "The user has not described a problem yet."

        llm_fields = await GeminiService.build_context_fields("\n".join(user_texts))
        if llm_fields:
            problem = llm_fields["problem"][:500]
            emotion = llm_fields["emotion"]
            goal = llm_fields["goal"]
            constraints = llm_fields["constraints"]
            summary = llm_fields["summary"]
        else:
            emotion = ContextService.detect_emotion(combined)
            goal = ContextService.detect_goal(combined)
            constraints = ContextService.detect_constraints(combined)
            problem = latest_text[:500]
            summary = (
                f"The user describes: {problem}. Main detected emotion: {emotion}. Main goal: {goal}."
            )

        existing_context = await ContextService.get_latest_context(db, session)
        if existing_context is None:
            context = ContextFile(
                session_id=session.id,
                problem=problem,
                emotion=emotion,
                goal=goal,
                constraints=constraints,
                summary=summary,
            )
            db.add(context)
        else:
            context = existing_context
            context.problem = problem
            context.emotion = emotion
            context.goal = goal
            context.constraints = constraints
            context.summary = summary
            db.add(context)

        await db.commit()
        await db.refresh(context)
        return context

    @staticmethod
    def detect_emotion(text: str) -> str:
        normalized = text.lower()
        if any(word in normalized for word in ["anxiety", "worry", "stress", "panic", "afraid"]):
            return "worry or stress"
        if any(word in normalized for word in ["confused", "lost", "unsure", "doubt"]):
            return "uncertainty"
        if any(word in normalized for word in ["tired", "exhausted", "burnout"]):
            return "tiredness"
        return "needs clarification"

    @staticmethod
    def detect_goal(text: str) -> str:
        normalized = text.lower()
        if any(word in normalized for word in ["goal", "plan", "improve", "habit"]):
            return "create a realistic action plan"
        if any(word in normalized for word in ["choose", "decision", "option"]):
            return "make a clearer decision"
        if any(word in normalized for word in ["anxiety", "worry", "stress", "panic"]):
            return "reduce pressure and choose a safe next step"
        return "understand the problem and find a first step"

    @staticmethod
    def detect_constraints(text: str) -> str:
        normalized = text.lower()
        constraints = []
        if any(word in normalized for word in ["time", "deadline", "busy"]):
            constraints.append("limited time")
        if any(word in normalized for word in ["money", "cost", "budget"]):
            constraints.append("limited budget")
        if any(word in normalized for word in ["fear", "afraid", "risk"]):
            constraints.append("fear of negative outcome")
        if not constraints:
            constraints.append("not enough structured information yet")
        return ", ".join(constraints)
