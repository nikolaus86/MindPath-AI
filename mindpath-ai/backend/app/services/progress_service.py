from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ProgressEntry, User


class ProgressService:
    @staticmethod
    def create_entry(
        db: Session, user: User, mood_score: int, note: str, session_id: int | None = None
    ) -> ProgressEntry:
        entry = ProgressEntry(
            user_id=user.id,
            session_id=session_id,
            mood_score=mood_score,
            note=note.strip(),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def list_entries(db: Session, user: User) -> list[ProgressEntry]:
        return list(
            db.scalars(
                select(ProgressEntry)
                .where(ProgressEntry.user_id == user.id)
                .order_by(ProgressEntry.created_at.desc())
            )
        )

    @staticmethod
    def average_mood(entries: list[ProgressEntry]) -> float | None:
        if not entries:
            return None
        return round(sum(entry.mood_score for entry in entries) / len(entries), 2)
