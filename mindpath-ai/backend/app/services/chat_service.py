from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Message, SessionModel, utc_now


class ChatService:
    @staticmethod
    def list_messages(db: Session, session: SessionModel) -> list[Message]:
        return list(
            db.scalars(
                select(Message)
                .where(Message.session_id == session.id)
                .order_by(Message.created_at.asc())
            )
        )

    @staticmethod
    def add_user_message(db: Session, session: SessionModel, text: str) -> tuple[Message, Message]:
        user_message = Message(session_id=session.id, role="user", text=text.strip())
        db.add(user_message)
        db.flush()

        reply = ChatService.make_assistant_reply(text)
        assistant_message = Message(session_id=session.id, role="assistant", text=reply)
        db.add(assistant_message)

        session.updated_at = utc_now()
        db.add(session)
        db.commit()
        db.refresh(user_message)
        db.refresh(assistant_message)
        return user_message, assistant_message

    @staticmethod
    def make_assistant_reply(text: str) -> str:
        normalized = text.lower()
        if any(word in normalized for word in ["anxiety", "worry", "stress", "panic"]):
            return "I saved your message. It sounds like stress or worry may be important here. We can build context and use the Anxiety Helper."
        if any(word in normalized for word in ["choose", "decision", "option", "unsure"]):
            return "I saved your message. This looks like a decision case, so we can compare options after building context."
        if any(word in normalized for word in ["goal", "plan", "improve", "habit"]):
            return "I saved your message. This looks suitable for a small planning flow after context building."
        return "I saved your message. Next, we can build a short context and choose a suitable mini-app."
