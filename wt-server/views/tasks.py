from flask import Blueprint, request, current_app
from ..models import db, nulls_first, order_random, order_desc
from ..models.word import Word, Spelling
from ..models.task import Task
from ..models.stats import WordStatistics
from ..services.tasks import TaskService
from ..services.stats import UserStatService

from marshmallow import Schema, fields
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import or_


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


@tasks_view.route('prepare')
@jwt_required()
def prepare_task():
    count = min(request.args.get('count', 20, type=int), 50)
    # errors = min(request.args.get('errors', 0, type=int), count)
    topics = request.args.getlist('topics[]', int)

    filters = []
    if len(topics) > 0:
        filters.append(
            or_(*[Word.topics.contains([topic]) for topic in topics])
        )

    data = UserStatService.get_user_words(
        current_user,
        count,
        filters,
        [order_desc(WordStatistics.failed)]
    ).scalars()
    return WordSchema().dump(data, many=True)
