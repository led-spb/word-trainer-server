from flask import Blueprint, request, current_app as app
from models.user import db, User, UserStat
from marshmallow import Schema, fields
from datetime import datetime
from flask_jwt_extended import jwt_required, current_user


users = Blueprint('users', __name__)

class UserSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    name = fields.Str(required=True)


@users.route('', methods=['GET'])
@jwt_required()
def get_user_info():
    return UserSchema().dump(current_user)

class UserStatSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    recorderd_at = fields.Date(required=True, dump_only=True)
    success = fields.List(fields.Int(), required=True)
    failed = fields.List(fields.Int(), required=True)


@users.route('/stat', methods=['GET'])
@jwt_required()
def get_user_stat():
    items = UserStat.query.filter(UserStat.user_id == current_user.id)
    return UserStatSchema().dump(items, many=True)


@users.route('/stat', methods=['PUT'])
@jwt_required()
def update_user_stat():
    data = UserStatSchema().load(request.get_json())

    stat = UserStat.query.filter(
        UserStat.user_id == current_user.id and UserStat.datetime == datetime.today()
    ).first()

    if stat is None:
        stat = UserStat(user_id=current_user.id, success=[], failed=[])

    success = stat.success[:]
    success.extend(data['success'])

    failed = stat.failed[:]
    failed.extend(data['failed'])

    stat.success = success
    stat.failed = failed

    app.logger.error(stat.success)
    app.logger.error(stat.failed)

    db.session.add(stat)
    db.session.commit()

    return '', 204
