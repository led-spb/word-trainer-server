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
        ).filter(
            Task.user_id == user.id
        )
        return db.session.execute(query).scalars()

    @classmethod
    def get_user_task(cls, user: User, task_id: int) -> Task|None:
        query = sa.select(
            Task
        ).filter(
            Task.user_id == user.id,
            Task.id == task_id
        )
        return db.session.execute(query).scalar_one_or_none()
