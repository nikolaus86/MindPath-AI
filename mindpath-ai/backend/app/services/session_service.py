from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import SessionModel, User, utc_now


class SessionService:
    @staticmethod
    def create_session(db: Session, user: User, title: str) -> SessionModel:
        clean_title = title.strip() or "New reflection"
        session = SessionModel(user_id=user.id, title=clean_title)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def list_sessions(db: Session, user: User) -> list[SessionModel]:
        return list(
            db.scalars(
                select(SessionModel)
                .where(SessionModel.user_id == user.id)
                .order_by(SessionModel.updated_at.desc())
            )
        )

    @staticmethod
    def get_owned_session(db: Session, user: User, session_id: int) -> SessionModel:
        session = db.get(SessionModel, session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    @staticmethod
    def touch(db: Session, session: SessionModel) -> None:
        session.updated_at = utc_now()
        db.add(session)
        db.commit()

    @staticmethod
    def delete_session(db: Session, user: User, session_id: int) -> None:
        session = SessionService.get_owned_session(db, user, session_id)
        db.delete(session)
        db.commit()
