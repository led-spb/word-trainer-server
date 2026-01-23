from typing import List, Union
from ..models import db
from ..models.word import Word, Tag, Rule
from sqlalchemy import func

class WordService:

    @classmethod
    def get_by_id(cls, word_id :int) -> Union[Word,None]:
        return db.session.execute(
            db.select(Word).filter(Word.id == word_id)
        ).scalar_one_or_none()

    @classmethod
    def find_by_name(cls, word_name: str, context :str = None) -> Union[Word,None]:
        query = db.select(
            Word
        ).filter(
            Word.fullword == word_name,
            Word.context == context,
        )
        return db.session.execute(query).scalar_one_or_none()

    @classmethod
    def get_total_words_count(cls) -> int:
        total_words, = db.session.execute(
            db.select(func.count(Word.id))
        ).one_or_none()

        return total_words

    @classmethod
    def get_tags_dictonary(cls) -> List[Tag]:
        tags = db.session.execute(
            db.select(Tag)
        ).scalars().all()

        return tags

    @classmethod
    def get_rule_by_id(cld, rule_id: int) -> Union[Rule,None]:
        return db.session.execute(
            db.select(Rule).filter(Rule.id == rule_id)
        ).scalar_one_or_none()
