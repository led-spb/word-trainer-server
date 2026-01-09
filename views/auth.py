from models.user import User
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, unset_access_cookies
from marshmallow import Schema, fields


auth = Blueprint('auth', __name__)


class UserLoginSchema(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)


def user_identity_lookup(user):
    return str(user.id)

def user_lookup(identity):
    return User.query.filter_by(id=identity).one_or_none()

@auth.route('/token', methods=['POST'])
def token():
    data = UserLoginSchema().load(request.get_json())

    auth_user = User.query.filter(User.name == data.get('login')).one_or_none()
    if auth_user is not None and auth_user.check_password(data.get('password')):
        access_token = create_access_token(identity=auth_user)
        #refresh_token = create_refresh_token(identity='default')

        response = jsonify({
            'access_token': access_token,
            #'refresh_token': refresh_token,
        })
        #set_access_cookies(response, access_token)
    else:
        response = jsonify({
            'error': 'Unkown user or bad password',
        })
        response.status_code = 401
    return response
