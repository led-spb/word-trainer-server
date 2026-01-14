from typing import Union, List
from ..models import db
from ..models.user import User, UserStat
from ..models.word import WordStatistics, Word
from datetime import date, timedelta
from sqlalchemy import cast, Numeric, desc, and_
from sqlalchemy.orm import joinedload


class UserService:

    @classmethod
    def get_user_by_id(cls, id :int) -> Union[User, None]:
        return db.session.execute(
            db.select(User).filter(User.id == id)
        ).scalar_one_or_none()
    
    @classmethod
    def get_user_by_login(cls, login :str) -> Union[User, None]:
        return db.session.execute(
            db.select(User).filter(User.name == login)
        ).scalar_one_or_none()


class UserStatService:

    @classmethod
    def get_user_word_failed(cls, user: User, count :int) -> List[WordStatistics]:
        query = db.select(
            WordStatistics
        ).options(
            joinedload(WordStatistics.word)
        ).filter(
            WordStatistics.user_id == user.id
        ).filter(
            WordStatistics.failed > 0
        ).order_by(
            cast(WordStatistics.success, Numeric) / (WordStatistics.success + WordStatistics.failed)
        ).order_by(
            desc(WordStatistics.failed)
        ).limit(count)

        return db.session.execute(query).scalars()


    @classmethod
    def get_user_stats(cls, user: User, days :int) -> List[UserStat]:
        query = db.select(UserStat
        ).filter(
            UserStat.user_id == user.id
        ).filter(
            UserStat.recorded_at >= date.today() - timedelta(days=days)
        )
        return db.session.execute(query).scalars()
        

    @classmethod
    def update_user_stat(cls, user: User, success: List[int], failed: List[int]) -> None:
        word_stats = db.session.execute(
            db.select(
                Word, WordStatistics
            ).outerjoin(
                WordStatistics,
                and_(
                    Word.id == WordStatistics.word_id,
                    WordStatistics.user_id == user.id
                )
            ).filter(
                Word.id.in_(success + failed)
            )
        )
        total_success = 0
        total_failed = 0

        for word, stat in word_stats:
            if stat is None:
                stat = WordStatistics(word_id=word.id, user_id=user.id, success=0, failed=0)
            if word.id in success:
                stat.success += 1
                total_success += 1
            if word.id in failed:
                stat.failed += 1
                total_failed += 1
            db.session.add(stat)

        user_stat = db.session.execute(
            db.select(
                UserStat
            ).filter(
                UserStat.user_id == user.id
            ).filter(
                UserStat.recorded_at == date.today()
            )
        ).scalar_one_or_none()

        if user_stat is None:
           user_stat = UserStat(user_id=user.id, success=total_success, failed=total_failed)
        else:
           user_stat.success += total_success
           user_stat.failed += total_failed

        db.session.add(user_stat)
        db.session.commit()
        return None
