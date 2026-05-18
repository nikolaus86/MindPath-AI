import json
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import MiniAppResult, SessionModel

MINI_APPS = {
    "problem-analysis": {
        "id": "problem-analysis",
        "title": "Problem Analysis",
        "description": "Structure the main problem and find a first small step.",
        "questions": [
            "What is the main problem?",
            "When did it start?",
            "What makes it difficult?",
            "What result would feel helpful?",
        ],
    },
    "anxiety-helper": {
        "id": "anxiety-helper",
        "title": "Anxiety Helper",
        "description": "Balance a worry with facts and choose one safe action.",
        "questions": [
            "What exactly are you worried about?",
            "What facts support this worry?",
            "What facts make it less certain?",
            "What is one safe small action today?",
        ],
    },
    "decision-assistant": {
        "id": "decision-assistant",
        "title": "Decision Assistant",
        "description": "Compare options, pros, cons, and the main risk.",
        "questions": [
            "What decision do you need to make?",
            "What options do you have?",
            "What are the pros and cons?",
            "What is the main risk?",
        ],
    },
    "goal-planner": {
        "id": "goal-planner",
        "title": "Goal Planner",
        "description": "Turn a goal into a short weekly action plan.",
        "questions": [
            "What goal do you want to reach?",
            "Why is it important?",
            "What deadline do you have?",
            "What are 3 small steps?",
        ],
    },
}


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
    def save_answers(
        db: Session, session: SessionModel, app_id: str, answers: dict[str, Any]
    ) -> MiniAppResult:
        MiniAppService.get_app(app_id)
        result_text = MiniAppService.generate_result(app_id, answers)
        result = MiniAppResult(
            session_id=session.id,
            app_id=app_id,
            answers_json=json.dumps(answers, ensure_ascii=False),
            result_text=result_text,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def list_results(db: Session, session: SessionModel) -> list[MiniAppResult]:
        return list(
            db.scalars(
                select(MiniAppResult)
                .where(MiniAppResult.session_id == session.id)
                .order_by(MiniAppResult.created_at.desc())
            )
        )

    @staticmethod
    def generate_result(app_id: str, answers: dict[str, Any]) -> str:
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
