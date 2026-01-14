from ..models import db
from ..models.word import Word


class WordService:

    @classmethod
    def find_by_name(cls, word_name: str) -> Word:
        query = db.select(
            Word
        ).filter(
            Word.fullword == word_name
        )
        return db.session.execute(query).scalar_one_or_none()
