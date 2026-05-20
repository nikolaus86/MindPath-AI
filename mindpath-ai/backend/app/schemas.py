from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class SessionCreate(BaseModel):
    title: str = "New reflection"


class SessionRead(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    text: str = Field(min_length=1, max_length=3000)


class MessageRead(BaseModel):
    id: int
    session_id: int
    role: str
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead
    suggested_app: str | None = None
    suggested_app_title: str | None = None


class ContextRead(BaseModel):
    id: int
    session_id: int
    problem: str
    emotion: str
    goal: str
    constraints: str
    summary: str
    recommended_app: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RouteResponse(BaseModel):
    recommended_app: str
    title: str
    reason: str
    context: ContextRead


class MiniAppDefinition(BaseModel):
    id: str
    title: str
    description: str
    questions: list[str]


class MiniAppStart(BaseModel):
    session_id: int


class MiniAppAnswer(BaseModel):
    session_id: int
    answers: dict[str, Any]


class MiniAppInsightResponse(BaseModel):
    insight: str
    llm_used: bool


class MiniAppResultRead(BaseModel):
    id: int
    session_id: int
    app_id: str
    answers_json: str
    result_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgressCreate(BaseModel):
    session_id: int | None = None
    mood_score: int = Field(ge=1, le=10)
    note: str = Field(default="", max_length=1000)


class ProgressRead(BaseModel):
    id: int
    user_id: int
    session_id: int | None
    mood_score: int
    note: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgressList(BaseModel):
    entries: list[ProgressRead]
    average_mood: float | None


class SummaryResponse(BaseModel):
    session: SessionRead
    context: ContextRead | None
    messages: list[MessageRead]
    mini_app_results: list[MiniAppResultRead]
    latest_result: MiniAppResultRead | None
    progress_entries: list[ProgressRead]
