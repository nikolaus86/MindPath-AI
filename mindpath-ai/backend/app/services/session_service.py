from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SessionModel, User, utc_now


class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, user: User, title: str) -> SessionModel:
        clean_title = title.strip() or "New reflection"
        session = SessionModel(user_id=user.id, title=clean_title)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def list_sessions(db: AsyncSession, user: User) -> list[SessionModel]:
        result = await db.scalars(
            select(SessionModel)
            .where(SessionModel.user_id == user.id)
            .order_by(SessionModel.updated_at.desc())
        )
        return list(result.all())

    @staticmethod
    async def get_owned_session(
        db: AsyncSession, user: User, session_id: int
    ) -> SessionModel:
        session = await db.get(SessionModel, session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    @staticmethod
    async def touch(db: AsyncSession, session: SessionModel) -> None:
        session.updated_at = utc_now()
        db.add(session)
        await db.commit()

    @staticmethod
    async def delete_session(db: AsyncSession, user: User, session_id: int) -> None:
        session = await SessionService.get_owned_session(db, user, session_id)
        await db.delete(session)
        await db.commit()
