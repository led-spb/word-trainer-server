from ..models import db
from ..models.word import Word
from sqlalchemy import func

class WordService:

    @classmethod
    def find_by_name(cls, word_name: str, context :str = None) -> Word:
        query = db.select(
            Word
        ).filter(
            Word.fullword == word_name,
            context is None or Word.context == context
        )
        return db.session.execute(query).scalar_one_or_none()

    @classmethod
    def get_total_words_count(cls) -> int:
        total_words, = db.session.execute(
            db.select(func.count(Word.id))
        ).one_or_none()

        return total_words
