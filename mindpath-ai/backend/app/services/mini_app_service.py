import json
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..mini_apps_catalog import MINI_APPS
from ..models import Message, MiniAppResult, SessionModel
from .llm_service import LlmService


class MiniAppService:
    @staticmethod
    def list_apps() -> list[dict[str, Any]]:
        return list(MINI_APPS.values())

    @staticmethod
    def get_app(app_id: str) -> dict[str, Any]:
        app = MINI_APPS.get(app_id)
        if app is None:
            raise HTTPException(status_code=404, detail="Mini-app not found")
        return app

    @staticmethod
    async def _session_chat_context(db: AsyncSession, session: SessionModel) -> str:
        result = await db.scalars(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at.asc())
            .limit(20)
        )
        messages = list(result.all())
        if not messages:
            return ""
        lines = []
        for message in messages:
            role = "User" if message.role == "user" else "Assistant"
            lines.append(f"{role}: {message.text}")
        return "\n".join(lines)

    @staticmethod
    async def request_insight(
        db: AsyncSession, session: SessionModel, app_id: str, answers: dict[str, Any]
    ) -> tuple[str, bool]:
        app = MiniAppService.get_app(app_id)
        context = await MiniAppService._session_chat_context(db, session)
        return await LlmService.mini_app_insight(
            app_id,
            app["title"],
            app["questions"],
            answers,
            session_context=context,
        )

    @staticmethod
    async def save_answers(
        db: AsyncSession, session: SessionModel, app_id: str, answers: dict[str, Any]
    ) -> MiniAppResult:
        app = MiniAppService.get_app(app_id)
        context = await MiniAppService._session_chat_context(db, session)
        result_text = await MiniAppService.generate_result(
            app_id, app, answers, session_context=context
        )
        result = MiniAppResult(
            session_id=session.id,
            app_id=app_id,
            answers_json=json.dumps(answers, ensure_ascii=False),
            result_text=result_text,
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result

    @staticmethod
    async def list_results(db: AsyncSession, session: SessionModel) -> list[MiniAppResult]:
        result = await db.scalars(
            select(MiniAppResult)
            .where(MiniAppResult.session_id == session.id)
            .order_by(MiniAppResult.created_at.desc())
        )
        return list(result.all())

    @staticmethod
    async def generate_result(
        app_id: str,
        app: dict[str, Any],
        answers: dict[str, Any],
        session_context: str = "",
    ) -> str:
        llm_text = await LlmService.mini_app_result(
            app_id,
            app["title"],
            app["questions"],
            answers,
            session_context=session_context,
        )
        if llm_text:
            return llm_text
        return MiniAppService._template_result(app_id, answers)

    @staticmethod
    def _template_result(app_id: str, answers: dict[str, Any]) -> str:
        values = [str(value).strip() for value in answers.values() if str(value).strip()]
        first = values[0] if values else "Not enough information"
        second = values[1] if len(values) > 1 else "Needs more detail"
        third = values[2] if len(values) > 2 else "Needs more detail"
        fourth = values[3] if len(values) > 3 else "Choose one small step"

        if app_id == "problem-analysis":
            return (
                f"Problem summary: {first}. Key difficulty: {third}. "
                f"First small step: write down what result would feel helpful and try one action connected to: {fourth}."
            )
        if app_id == "anxiety-helper":
            return (
                f"Balanced thought: the worry is about {first}. There are reasons to take it seriously: {second}. "
                f"At the same time, it may be less certain because: {third}. Small action plan: {fourth}."
            )
        if app_id == "decision-assistant":
            return (
                f"Comparison summary: the decision is {first}. Main options: {second}. "
                f"Pros and cons to review: {third}. Suggested next step: reduce the main risk by testing one option safely. Main risk: {fourth}."
            )
        if app_id == "goal-planner":
            return (
                f"Weekly action plan: focus on {first} because {second}. Deadline: {third}. "
                f"First task: start with one of these small steps: {fourth}."
            )
        return "The result was saved."
