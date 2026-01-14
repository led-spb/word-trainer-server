from flask import Blueprint, request, current_app as app
from marshmallow import Schema, fields
from ..models import db
from ..models.word import Word, Accent
from ..services.words import WordService
from ..services.tasks import TaskService
from .words import WordSchema
from flask_jwt_extended import jwt_required, current_user


accents = Blueprint('accents', __name__)


class AccentImportSchema(Schema):
    words = fields.List(fields.String, required=True)
    level = fields.Int(required=True)

class AccentPositionSchema(Schema):
    position = fields.Int()
    
class AccentSchema(WordSchema):
    accents = fields.Pluck(AccentPositionSchema, 'position', many=True)

class AccentImportResultSchema(Schema):
    results = fields.Nested(AccentSchema, many=True)


#@accents.route('/import', methods=['POST'])
def import_accent():
    data = AccentImportSchema().load(
        request.get_json()
    )
    word_level = data.get('level', 6)

    results = []
    for item in data.get('words', []):
        accent_position = next((idx for idx, chr in enumerate(item) if chr.isupper()), None)
        word = None
        if accent_position is not None:
            word = WordService.find_by_name(item.lower())
            if word is None:
                word = Word(fullword=item.lower(), level=word_level)
                db.session.add(word)

            acc_positions = [acc.position for acc in word.accents]
            if accent_position not in acc_positions:
                word.accents.append(
                    Accent(word_id=word.id, position=accent_position)
                )
                db.session.add(word)
        results.append(word)

    db.session.commit()
    return AccentImportResultSchema().dump({'results': results}), 200


@accents.route('/task', methods=['GET'])
@jwt_required()
def prepare_task():
    min_level = request.args.get('min', 1, type=int)
    max_level = request.args.get('max', 10, type=int)
    count = min(request.args.get('count', 20, type=int), 50)

    task = TaskService.get_user_accent_task(current_user, count=count, min_level=min_level, max_level=max_level)
    return AccentSchema().dump(task, many=True)
