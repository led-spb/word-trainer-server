from flask import Blueprint, abort, request, current_app as app, jsonify
from marshmallow import Schema, fields
from ..services.words import WordService
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

rules = Blueprint('rules', __name__)


class RuleSchema(Schema):
    id = fields.Integer()
    description = fields.String()


@rules.route('<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id: int):
    rule = WordService.get_rule_by_id(rule_id)
    if rule is None:
        abort(404)
    return RuleSchema().dump(rule)
