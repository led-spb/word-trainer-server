from ..models import db
from ..models.user import User
from ..models.task import Task
from datetime import date, timedelta
import sqlalchemy as sa
from typing import Sequence, Iterator

class TaskService:

    @classmethod
    def get_user_tasks(cls, user: User) -> Iterator[Task]:
        query = sa.select(
            Task
        )
        return db.session.execute(query).scalars()
