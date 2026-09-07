from enum import Enum
from . import Base
from typing import List
from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    repeat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    topics: Mapped[List['int']] = mapped_column(JSONB, nullable=True, default='[]')
    executed_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now(), nullable=True)
