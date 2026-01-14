from typing import List, Union
from ..models import db
from ..models.word import Word, Accent
from sqlalchemy import func, and_, nulls_first
from sqlalchemy.orm import joinedload, selectinload


class AccentService:

    @classmethod
    def find_by_word(cls, word: str) -> List[Word]:
        query = db.select(
            Word
        ).options(
            joinedload(Word.accents)
        ).filter(
            Word.accents.any()
        ).filter(
            Word.fullword == word.lower()
        )
        return db.session.execute(query).scalars().all()


