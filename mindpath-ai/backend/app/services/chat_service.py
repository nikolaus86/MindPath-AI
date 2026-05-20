from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Message, SessionModel, utc_now
from ..mini_apps_catalog import MINI_APPS
from .llm_service import LlmService


class ChatService:
    @staticmethod
    async def list_messages(db: AsyncSession, session: SessionModel) -> list[Message]:
        result = await db.scalars(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at.asc())
        )
        return list(result.all())

    @staticmethod
    async def add_user_message(
        db: AsyncSession, session: SessionModel, text: str
    ) -> tuple[Message, Message, str | None]:
        user_message = Message(session_id=session.id, role="user", text=text.strip())
        db.add(user_message)
        await db.flush()

        prior = await ChatService.list_messages(db, session)
        history = [(message.role, message.text) for message in prior if message.id != user_message.id]

        reply, suggested_app, _used_llm = await LlmService.chat_reply(
            history=history,
            user_text=user_message.text,
            session_title=session.title,
        )

        if suggested_app and suggested_app in MINI_APPS:
            app_title = MINI_APPS[suggested_app]["title"]
            if app_title.lower() not in reply.lower():
                reply = f"{reply}\n\nRecommended mini-app: {app_title} — open it when you're ready."

        assistant_message = Message(session_id=session.id, role="assistant", text=reply)
        db.add(assistant_message)

        session.updated_at = utc_now()
        db.add(session)
        await db.commit()
        await db.refresh(user_message)
        await db.refresh(assistant_message)
        return user_message, assistant_message, suggested_app
