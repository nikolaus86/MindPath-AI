import json
import logging
import os
import re
from typing import Any, Literal

import httpx

from .. import env as _env  # noqa: F401 — load .env on import
from ..mini_apps_catalog import MINI_APPS

logger = logging.getLogger(__name__)

ProviderName = Literal["ai_gateway", "none"]

AI_GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
DEFAULT_AI_GATEWAY_MODEL = "openai/gpt-4o-mini"

VALID_APP_IDS = frozenset(MINI_APPS.keys())

MINI_APPS_CATALOG = "\n".join(
    f'- "{app["id"]}": {app["title"]} — {app["description"]}'
    for app in MINI_APPS.values()
)

CHAT_SYSTEM_PROMPT = f"""You are MindPath AI, a calm and supportive self-reflection assistant.
Help the user explore feelings, clarify their situation, and find a small next step.
Never give medical diagnoses or crisis instructions; encourage professional help for emergencies.

Available mini-apps (use exact id when recommending):
{MINI_APPS_CATALOG}

Rules:
- Reply in the same language as the user's latest message.
- Keep replies concise (2–5 sentences), warm and practical.
- When the situation is clear enough, recommend exactly one mini-app and mention its title.
- If you need more information, ask one focused question and set suggested_app to null.
- Respond ONLY with valid JSON, no markdown fences."""

ROUTER_SYSTEM_PROMPT = f"""You are MindPath AI router. Pick the best mini-app for this reflection session.

Available mini-apps (use exact id):
{MINI_APPS_CATALOG}

Rules:
- Choose exactly one app_id from the list above.
- Write reason in the same language as the session context (1–2 sentences).
- Respond ONLY with valid JSON: {{"app_id": "<id>", "reason": "<text>"}}"""

CONTEXT_SYSTEM_PROMPT = """You analyze a self-reflection chat and extract structured context.
Respond ONLY with valid JSON:
{
  "problem": "<main problem in 1-3 sentences>",
  "emotion": "<dominant emotion or feeling>",
  "goal": "<what the user wants to achieve>",
  "constraints": "<limitations, fears, time, money — comma-separated>",
  "summary": "<2-3 sentence summary>"
}
Use the same language as the user's messages."""

MINI_APP_SYSTEM_PROMPT = """You are MindPath AI. The user completed a guided mini-app exercise.
Write a personalized, practical result: empathetic analysis and 1-3 concrete next steps.
Use the same language as the user's answers. Plain text only, no JSON, 3-8 sentences."""

MINI_APP_INSIGHT_PROMPT = """You are MindPath AI. The user is filling in a guided mini-app exercise.
Based on their answers so far (some fields may still be empty), give a helpful insight:
- briefly reflect what stands out in their situation
- name one useful pattern, tension, or strength you notice
- suggest what to clarify next or one small step to consider
Use the same language as the user's answers. Plain text only, no JSON, 3-6 sentences."""


class LlmService:
    @staticmethod
    def ai_gateway_api_key() -> str:
        # Vercel docs use AI_GATEWAY_API_KEY. VERCEL_AI_GATEWAY_API_KEY is also
        # accepted so students can name the variable explicitly in local demos.
        return (
            os.getenv("AI_GATEWAY_API_KEY", "").strip()
            or os.getenv("VERCEL_AI_GATEWAY_API_KEY", "").strip()
        )

    @staticmethod
    def provider() -> ProviderName:
        return "ai_gateway" if LlmService.ai_gateway_api_key() else "none"

    @staticmethod
    def model() -> str | None:
        if LlmService.provider() == "ai_gateway":
            return os.getenv("AI_GATEWAY_MODEL", DEFAULT_AI_GATEWAY_MODEL).strip() or DEFAULT_AI_GATEWAY_MODEL
        return None

    @staticmethod
    def is_configured() -> bool:
        return LlmService.provider() != "none"

    @staticmethod
    async def chat_reply(
        history: list[tuple[str, str]],
        user_text: str,
        session_title: str = "",
    ) -> tuple[str, str | None, bool]:
        if not LlmService.is_configured():
            reply, app = LlmService._fallback_chat_reply(user_text)
            return reply, app, False

        prompt = LlmService._build_chat_prompt(history, user_text, session_title)
        try:
            raw = await LlmService._generate(
                system_instruction=CHAT_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.7,
                json_mode=True,
            )
            reply, app = LlmService._parse_chat_response(raw, user_text)
            return reply, app, True
        except Exception as exc:
            logger.exception("%s chat request failed", LlmService.provider())
            # Keep the demo usable during network/API-key problems. The user still
            # gets a practical reply and the frontend can auto-open the mini-app.
            reply, app = LlmService._fallback_chat_reply(user_text)
            return f"{reply} (AI Gateway fallback: {LlmService._friendly_error(exc)})", app, False

    @staticmethod
    async def route_session(context_text: str) -> tuple[str, str, bool]:
        if not LlmService.is_configured():
            app_id, reason = LlmService._fallback_route(context_text)
            return app_id, reason, False

        prompt = (
            "Session context:\n"
            f"{context_text}\n\n"
            "Pick the most suitable mini-app for this user right now."
        )
        try:
            raw = await LlmService._generate(
                system_instruction=ROUTER_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.2,
                json_mode=True,
            )
            app_id, reason = LlmService._parse_route_response(raw, context_text)
            return app_id, reason, True
        except Exception as exc:
            logger.exception("%s router request failed", LlmService.provider())
            app_id, reason = LlmService._fallback_route(context_text)
            reason = f"{reason} ({LlmService._friendly_error(exc)})"
            return app_id, reason, False

    @staticmethod
    async def build_context_fields(conversation: str) -> dict[str, str] | None:
        if not LlmService.is_configured() or not conversation.strip():
            return None
        try:
            raw = await LlmService._generate(
                system_instruction=CONTEXT_SYSTEM_PROMPT,
                user_prompt=f"User messages from the session:\n\n{conversation}",
                temperature=0.3,
                json_mode=True,
            )
            data = LlmService._load_json(raw)
            fields = {
                "problem": str(data.get("problem", "")).strip(),
                "emotion": str(data.get("emotion", "")).strip(),
                "goal": str(data.get("goal", "")).strip(),
                "constraints": str(data.get("constraints", "")).strip(),
                "summary": str(data.get("summary", "")).strip(),
            }
            if fields["problem"] and fields["summary"]:
                return fields
        except Exception:
            logger.exception("%s context build failed", LlmService.provider())
        return None

    @staticmethod
    def _answer_for_question(answers: dict[str, Any], index: int, question: str) -> str:
        candidates = (
            f"q{index + 1}",
            str(index),
            str(index + 1),
            question,
        )
        for key in candidates:
            if key in answers and str(answers[key]).strip():
                return str(answers[key]).strip()
        for k, v in answers.items():
            if str(v).strip() and str(k).lower() in question.lower()[:24]:
                return str(v).strip()
        return ""

    @staticmethod
    def _format_mini_app_qa(questions: list[str], answers: dict[str, Any]) -> list[str]:
        lines = []
        for index, question in enumerate(questions):
            answer = LlmService._answer_for_question(answers, index, question)
            lines.append(f"Q: {question}\nA: {answer or '(not answered yet)'}")
        return lines

    @staticmethod
    def _has_any_answer(questions: list[str], answers: dict[str, Any]) -> bool:
        return any(
            LlmService._answer_for_question(answers, i, q) for i, q in enumerate(questions)
        )

    @staticmethod
    async def mini_app_insight(
        app_id: str,
        app_title: str,
        questions: list[str],
        answers: dict[str, Any],
        session_context: str = "",
    ) -> tuple[str, bool]:
        if not LlmService._has_any_answer(questions, answers):
            return "Fill in at least one answer to get an insight.", False

        if not LlmService.is_configured():
            return LlmService._fallback_mini_app_insight(questions, answers), False

        qa_block = "\n\n".join(LlmService._format_mini_app_qa(questions, answers))
        context_block = ""
        if session_context.strip():
            context_block = f"Earlier chat context from this session:\n{session_context.strip()}\n\n"

        prompt = (
            f"Mini-app: {app_title} ({app_id})\n\n"
            f"{context_block}"
            f"Current answers:\n{qa_block}\n\n"
            "Give an insight for the user based on what they shared so far."
        )
        try:
            text = await LlmService._generate(
                system_instruction=MINI_APP_INSIGHT_PROMPT,
                user_prompt=prompt,
                temperature=0.65,
                json_mode=False,
            )
            return text, True
        except Exception as exc:
            logger.exception("%s mini-app insight failed", LlmService.provider())
            return LlmService._llm_unavailable_message(exc), False

    @staticmethod
    async def mini_app_result(
        app_id: str,
        app_title: str,
        questions: list[str],
        answers: dict[str, Any],
        session_context: str = "",
    ) -> str | None:
        if not LlmService.is_configured():
            return None

        if not LlmService._has_any_answer(questions, answers):
            return None

        qa_block = "\n\n".join(LlmService._format_mini_app_qa(questions, answers))
        context_block = ""
        if session_context.strip():
            context_block = f"Earlier chat context:\n{session_context.strip()}\n\n"

        prompt = (
            f"Mini-app: {app_title} ({app_id})\n\n"
            f"{context_block}"
            f"{qa_block}\n\n"
            "Write the personalized final result for the user."
        )
        try:
            return await LlmService._generate(
                system_instruction=MINI_APP_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.6,
                json_mode=False,
            )
        except Exception:
            logger.exception("%s mini-app result failed", LlmService.provider())
            return None

    @staticmethod
    def _fallback_mini_app_insight(questions: list[str], answers: dict[str, Any]) -> str:
        filled = [
            LlmService._answer_for_question(answers, i, q)
            for i, q in enumerate(questions)
            if LlmService._answer_for_question(answers, i, q)
        ]
        preview = filled[0][:200] if filled else ""
        return (
            f"From what you shared: «{preview}». "
            "Consider what feels most important right now and complete the remaining questions "
            "before saving the final result."
        )

    @staticmethod
    async def _generate(
        *,
        system_instruction: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool = False,
    ) -> str:
        provider = LlmService.provider()
        if provider == "ai_gateway":
            return await LlmService._generate_ai_gateway(
                system_instruction=system_instruction,
                user_prompt=user_prompt,
                temperature=temperature,
                json_mode=json_mode,
            )
        raise RuntimeError("No LLM provider configured")

    @staticmethod
    async def _generate_ai_gateway(
        *,
        system_instruction: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool,
    ) -> str:
        """Generate text through Vercel AI Gateway using its OpenAI-compatible API."""
        payload: dict[str, Any] = {
            "model": LlmService.model(),
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 2048,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AI_GATEWAY_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LlmService.ai_gateway_api_key()}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "MindPath AI",
                },
                json=payload,
            )
            if response.is_error:
                LlmService._raise_for_status(response, provider="ai_gateway")
            data = response.json()

        choices = data.get("choices") or []
        if not choices:
            raise ValueError("AI Gateway returned no choices")

        text = (choices[0].get("message") or {}).get("content", "").strip()
        if not text:
            raise ValueError("AI Gateway returned empty text")
        return text

    @staticmethod
    def _raise_for_status(response: httpx.Response, *, provider: str) -> None:
        try:
            body = response.json()
            message = body.get("error", {}).get("message", response.text)
        except Exception:
            message = response.text
        raise httpx.HTTPStatusError(
            message,
            request=response.request,
            response=response,
        )

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        provider = LlmService.provider()
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            try:
                body = exc.response.json()
                msg = body.get("error", {}).get("message", str(exc))
            except Exception:
                msg = str(exc)
            if status == 429:
                return "rate limit exceeded — check Vercel AI Gateway usage or wait"
            if status == 400 and "location" in msg.lower():
                return "API not available in your region"
            if status in {401, 403}:
                return "invalid or unauthorized AI Gateway API key"
            if status == 404:
                return "model not found — check AI_GATEWAY_MODEL"
            return msg[:200] or f"HTTP {status}"
        return str(exc)[:200]

    @staticmethod
    def _llm_unavailable_message(exc: Exception) -> str:
        hint = LlmService._friendly_error(exc)
        return (
            "AI Gateway is temporarily unavailable. "
            f"Reason: {hint}. "
            "Check AI_GATEWAY_API_KEY / AI_GATEWAY_MODEL in backend/.env, "
            "restart the backend, and try again."
        )

    @staticmethod
    def _build_chat_prompt(
        history: list[tuple[str, str]],
        user_text: str,
        session_title: str,
    ) -> str:
        lines = []
        if session_title:
            lines.append(f"Session title: {session_title}")
        if history:
            lines.append("Conversation so far:")
            for role, content in history[-12:]:
                label = "User" if role == "user" else "Assistant"
                lines.append(f"{label}: {content}")
        lines.append(f'Latest user message: "{user_text}"')
        lines.append(
            'Return JSON: {"reply": "<assistant message>", "suggested_app": "<app_id or null>"}'
        )
        return "\n".join(lines)

    @staticmethod
    def _parse_chat_response(raw: str, user_text: str) -> tuple[str, str | None]:
        data = LlmService._load_json(raw)
        reply = str(data.get("reply", "")).strip()
        suggested = data.get("suggested_app")
        if suggested is not None:
            suggested = str(suggested).strip() or None
            if suggested and suggested.lower() in {"null", "none"}:
                suggested = None
        if suggested and suggested not in VALID_APP_IDS:
            suggested = None
        if not reply:
            return LlmService._fallback_chat_reply(user_text)
        return reply, suggested

    @staticmethod
    def _parse_route_response(raw: str, context_text: str) -> tuple[str, str]:
        data = LlmService._load_json(raw)
        app_id = str(data.get("app_id", "")).strip()
        reason = str(data.get("reason", "")).strip()
        if app_id not in VALID_APP_IDS:
            return LlmService._fallback_route(context_text)
        if not reason:
            reason = f"Recommended {MINI_APPS[app_id]['title']} based on the session context."
        return app_id, reason

    @staticmethod
    def _load_json(raw: str) -> dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)

    @staticmethod
    def _fallback_chat_reply(user_text: str) -> tuple[str, str | None]:
        normalized = user_text.lower()
        if any(word in normalized for word in ["anxiety", "worry", "stress", "panic", "тревог", "волную", "стресс"]):
            return (
                "I hear that stress or worry is present. When you're ready, use Build context "
                "and try the Anxiety Helper mini-app.",
                "anxiety-helper",
            )
        if any(word in normalized for word in ["choose", "decision", "option", "unsure", "выбор", "решени"]):
            return (
                "This sounds like a decision situation. Build context first, then open "
                "the Decision Assistant to compare your options.",
                "decision-assistant",
            )
        if any(word in normalized for word in ["goal", "plan", "improve", "habit", "цель", "план"]):
            return (
                "Planning could help here. After building context, try the Goal Planner "
                "to break this into small steps.",
                "goal-planner",
            )
        return (
            "Thank you for sharing. Tell me a bit more, or use Build context and "
            "Problem Analysis to structure the situation.",
            "problem-analysis",
        )

    @staticmethod
    def _fallback_route(context_text: str) -> tuple[str, str]:
        normalized = context_text.lower()
        if any(word in normalized for word in ["anxiety", "worry", "stress", "panic", "afraid", "тревог"]):
            return "anxiety-helper", "The session mentions worry, stress, or anxiety."
        if any(word in normalized for word in ["choose", "decision", "option", "unsure", "выбор"]):
            return "decision-assistant", "The session is about choosing between options."
        if any(word in normalized for word in ["goal", "plan", "improve", "habit", "цель", "план"]):
            return "goal-planner", "The session focuses on goals and planning."
        return "problem-analysis", "The session needs basic problem structuring first."


# Backward-compatible alias used across the codebase
AIService = LlmService
