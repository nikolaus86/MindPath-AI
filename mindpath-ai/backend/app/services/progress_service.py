from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ProgressEntry, User


class ProgressService:
    @staticmethod
    async def create_entry(
        db: AsyncSession,
        user: User,
        mood_score: int,
        note: str,
        session_id: int | None = None,
    ) -> ProgressEntry:
        entry = ProgressEntry(
            user_id=user.id,
            session_id=session_id,
            mood_score=mood_score,
            note=note.strip(),
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def list_entries(db: AsyncSession, user: User) -> list[ProgressEntry]:
        result = await db.scalars(
            select(ProgressEntry)
            .where(ProgressEntry.user_id == user.id)
            .order_by(ProgressEntry.created_at.desc())
        )
        return list(result.all())

    @staticmethod
    def average_mood(entries: list[ProgressEntry]) -> float | None:
        if not entries:
            return None
        return round(sum(entry.mood_score for entry in entries) / len(entries), 2)
