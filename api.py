import flask
from views import *


def create_api(app: flask.Flask) -> flask.Flask:
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(users, url_prefix='/api/user')
    #app.register_blueprint(words, url_prefix='/api/words')
    app.register_blueprint(spellings, url_prefix='/api/spellings')

    return app
