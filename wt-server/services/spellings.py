from typing import List
from ..models import db
from ..models.user import User
from ..models.word import Word, WordStatistics, Spelling
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
import difflib


class SpellingService:

    @classmethod
    def find_by_word(cls, word: str, context :str = None) -> List[Word]:
        query = db.select(
            Word
        ).options(
            joinedload(Word.spellings)
        ).filter(
            Word.spellings.any()
        ).filter(
            Word.fullword == word.lower(),
            context is None or Word.context == context,
        )
        return db.session.execute(query).scalars().all()

    @classmethod
    def get_with_user_stats(cls, user: User, filters: List, order_by: List, count: int) -> List[Word]:
        query = db.select(Word).options(
            joinedload(Word.spellings)
        ).outerjoin(
            WordStatistics,
            and_(
                WordStatistics.word_id == Word.id,
                WordStatistics.user_id == user.id
            )
        ).filter(
            Word.spellings.any()
        ).filter(
            *filters
        ).order_by(
            *order_by
        ).limit(
            count
        )
        return db.session.execute(query).unique().scalars().all()

    @classmethod
    def import_spelling(cls, word :Word, variant :str) -> Word:
        if variant == '':
            return word

        matcher = difflib.SequenceMatcher()
        matcher.set_seqs(word.fullword, variant)

        for action in matcher.get_opcodes():
            if action[0] == 'equal':
                continue

            variant1 = word.fullword[action[1]:action[2]]
            variant2 = variant[action[3]:action[4]]
            
            spelling = Spelling(
                position=action[1],
                length=action[2]-action[1],
                variants=[
                    '_' if variant1 == '' else variant1,
                    '_' if variant2 == '' else variant2
                ]
            )
            cls.add_word_spelling(word, spelling)
        db.session.add(word)
        db.session.commit()
        return word
    
    @classmethod
    def add_word_spelling(cls, word :Word, spelling :Spelling):
        for item in word.spellings:
            if item.position == spelling.position and item.length == spelling.length:
                new_variants = list(set(item.variants + spelling.variants))
                item.variants = new_variants
                return word
        word.spellings.append(spelling)
