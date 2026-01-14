import flask
from marshmallow.exceptions import ValidationError
from .views import *


def create_api(app: flask.Flask) -> flask.Flask:
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(users, url_prefix='/api/user')
    app.register_blueprint(spellings, url_prefix='/api/spellings')
    app.register_blueprint(accents, url_prefix='/api/accents')

    @app.errorhandler(ValidationError)
    def on_validation_error(e):
        return flask.jsonify({'code': 'ValidationError', 'messages':e.messages}), 400

    return app
