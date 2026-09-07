from flask import Blueprint, request, abort
from ..models import db, order_random, order_desc
from ..models.user import User
from ..models.word import Word
from ..models.task import Task
from ..models.stats import WordStatistics
from ..services.tasks import TaskService
from ..services.stats import UserStatService
from datetime import datetime
from marshmallow import Schema, fields
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import or_
from typing import Iterable


tasks_view = Blueprint('tasks', __name__)


class SpellingSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    position = fields.Int(required=True)
    length = fields.Int(required=True)
    variants = fields.List(fields.Str())

class AccentPositionSchema(Schema):
    position = fields.Int()

class WordSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    fullword = fields.Str(required=True)
    context = fields.Str()
    description = fields.Str()
    level = fields.Int(required=True)
    rules = fields.List(fields.Integer())
    topics = fields.List(fields.Integer())
    spellings = fields.Nested(SpellingSchema, many=True, dump_only=True)
    accents = fields.Pluck(AccentPositionSchema, 'position', many=True)

class TaskSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    executed_at = fields.DateTime()
    word_count = fields.Int()
    repeat_count = fields.Int()
    topics = fields.List(fields.Int())

@tasks_view.route('')
@jwt_required()
def get_user_tasks():
    tasks = TaskService.get_user_tasks(current_user)
    return TaskSchema().dump(tasks, many=True)


def make_user_task(user: User, topics: list[int], word_count: int, repeat_count: int) -> Iterable[Word]:
    default_filters = []
    if len(topics) > 0:
        default_filters.append(
            or_(*[Word.topics.contains([topic]) for topic in topics])
        )

    words = []
    if repeat_count > 0:
        repeats = UserStatService.get_user_words(
            current_user,
            repeat_count,
            default_filters+[WordStatistics.failed > 0],
            [order_random()]
        ).scalars()
        words.extend(repeats)

    data = UserStatService.get_user_words(
        current_user,
        word_count-len(words),
        default_filters,
        [order_random()]
    ).scalars()
    words.extend(data)
    return words

@tasks_view.route('<int:task_id>', methods=['GET'])
@jwt_required()
def get_task_content(task_id: int):
    task = TaskService.get_user_task(current_user, task_id)
    if task is None:
        abort(404)

    words = make_user_task(
        user=current_user,
        topics=task.topics,
        word_count=task.word_count,
        repeat_count=task.repeat_count
    )
    return WordSchema().dump(words, many=True)

@tasks_view.route('<int:task_id>/complete', methods=['PUT'])
@jwt_required()
def complete_task(task_id: int):
    task = TaskService.get_user_task(current_user, task_id)
    if task is None:
        abort(404)
    task.executed_at = datetime.now()
    db.session.add(task)
    db.session.commit()
    return '', 204


@tasks_view.route('prepare', methods=['GET'])
@jwt_required()
def prepare_task():
    word_count = min(request.args.get('word_count', 20, type=int), 50)
    repeat_count = min(request.args.get('repeat_count', 0, type=int), word_count)
    topics = request.args.getlist('topics[]', int)

    words = make_user_task(
        user=current_user,
        topics=topics,
        word_count=word_count,
        repeat_count=repeat_count
    )
    return WordSchema().dump(words, many=True)
