from typing import List
from models import db
from models.user import User
from models.word import Word, WordStatistics
from sqlalchemy import func, and_, nulls_first
from sqlalchemy.orm import joinedload, selectinload


class TaskService:

    @classmethod
    def get_user_spelling_task(cls, user :User, count: int = 20, min_level :int = 0, max_level :int = 10) -> List[Word]:
        query = db.select(
            Word
        ).options(
            joinedload(Word.spellings)
        ).outerjoin(
            WordStatistics,
            and_(
                Word.id == WordStatistics.word_id,
                WordStatistics.user_id == user.id
            )
        ).filter(
            Word.spellings.any()
        ).filter(
            Word.level >= min_level
        ).filter(
            Word.level <= max_level
        ).order_by(
            nulls_first(WordStatistics.failed+WordStatistics.success), func.random()
        ).limit(
            count
        )
        return db.session.execute(query).unique().scalars()
