from flask import Blueprint, request
from models.words import db, Word, Spelling
from sqlalchemy import func
from marshmallow import Schema, fields
from flask_jwt_extended import jwt_required, current_user


spellings = Blueprint('spellings', __name__)


class SpellingSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    position = fields.Int(required=True)
    length = fields.Int(required=True)
    variants = fields.List(fields.Str())


class WordSpellingSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    fullword = fields.Str(required=True)
    context = fields.Str()
    description = fields.Str()
    level = fields.Int(required=True)
    spellings = fields.Nested(SpellingSchema, many=True, dump_only=True)


@spellings.route('<int:word_id>', methods=['GET'])
def get_word_spellings(word_id):
     items = Spelling.query.filter(Spelling.word_id == word_id)
     return SpellingSchema().dump(items, many=True)


@spellings.route('<int:word_id>', methods=['POST'])
def create_word_spelling(word_id):
     word = Word.query.get_or_404(word_id)

     data = SpellingSchema().load(request.get_json())
     spelling = Spelling(**data)
     spelling.word_id = word.id
     db.session.add(spelling)
     db.session.commit()

     return get_word_spellings(word_id)


@spellings.route('part/<int:id>', methods=['DELETE'])
def delete_word_spelling(id):
    part = Spelling.query.get_or_404(id)
    db.session.delete(part)
    db.session.commit()
    return '', 204


@spellings.route('task/<int:task_id>')
@jwt_required()
def get_task(task_id):
    page = request.args.get('page', 1, type=int)

    seed_value = 2/task_id - 1

    db.session.execute(
         func.setseed(seed_value)
    )
    items = db.paginate(
        Word.query.
            filter(Word.spellings.any()).
            order_by(func.random()),

        page=page, per_page=20
    )
    return WordSpellingSchema().dump(items, many=True)
