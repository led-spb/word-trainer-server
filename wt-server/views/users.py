from flask import Blueprint, jsonify, request, current_app as app
from ..services.users import UserStatService
from marshmallow import Schema, fields
from flask_jwt_extended import jwt_required, current_user


users = Blueprint('users', __name__)

class UserSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    name = fields.Str(required=True)


@users.route('', methods=['GET'])
@jwt_required()
def get_user_info():
    return UserSchema().dump(current_user)

class AccentSchema(Schema):
    position = fields.Int()

class SpellingSchema(Schema):
    position = fields.Int()
    length = fields.Int()

class WordSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    fullword = fields.Str(required=True)
    context = fields.Str()
    description = fields.Str()
    level = fields.Int(required=True)
    spellings = fields.Nested(SpellingSchema, many=True)
    accents = fields.Pluck(AccentSchema, 'position', many=True)

class WordStatSchema(Schema):
    word = fields.Nested(WordSchema)
    success = fields.Int()
    failed = fields.Int()
    precent = fields.Method("get_precent")

    def get_precent(self, obj):
        return obj.success / (obj.success + obj.failed)

class DayStatSchema(Schema):
    recorded_at = fields.Date()
    success = fields.Int()
    failed = fields.Int()

class UserStatSchema(Schema):
    failed = fields.Nested(WordStatSchema, many=True)
    days = fields.Nested(DayStatSchema, many=True)

class UpdateUserStateSchema(Schema):
    failed = fields.List(fields.Int)
    success = fields.List(fields.Int)


@users.route('/stat', methods=['GET'])
@jwt_required()
def get_user_stat():
    failed_words = UserStatService.get_user_word_failed(current_user, count=10)
    stats = UserStatService.get_user_stats(current_user, days=14)

    return UserStatSchema().dump({
        'failed': failed_words,
        'days': stats
    })


class UserRatingSchema(Schema):
    user = fields.Nested(UserSchema)
    success = fields.Integer()
    failed = fields.Integer()
    total = fields.Integer()


@users.route('/rating', methods=['GET'])
@jwt_required()
def get_rating():
    days = min(request.args.get('days', 7, type=int), 90)
    count = min(request.args.get('count', 5, type=int), 10)
    
    stat = UserStatService.get_users_with_aggregate_stat(days=days, count=count)
    return UserRatingSchema().dump(
        [
            dict(
                user=user, 
                success=success,
                failed=failed,
                total=total
            ) 
            for (user, success, failed, total) in stat 
        ],
        many=True
    )

@users.route('/stat', methods=['PUT'])
@jwt_required()
def update_user_stat():
    data = UpdateUserStateSchema().load(
        request.get_json()
    )
    UserStatService.update_user_stat(
        current_user, 
        success=data.get('success', []), 
        failed=data.get('failed', [])
    )
    return '', 204
