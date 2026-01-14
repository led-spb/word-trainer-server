from flask import Flask
from flask_jwt_extended import JWTManager
from .views.auth import user_identity_lookup, user_lookup
import click


def create_app(config_filename='config.py'):
    app = Flask(__name__)

    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def identity_loader(user):
        return user_identity_lookup(user)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return user_lookup(identity)

    app.config.from_pyfile(config_filename)

    from .models import db
    db.init_app(app)

    from .api import create_api
    create_api(app)

    @app.cli.command("init-db")
    def init_db():
        db.create_all()


    @app.cli.command("create-user")
    @click.option('--name', help='User name')
    @click.option('--password', help='User password')
    def create_user(name, password):
        from .models.user import User

        user = User(name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    return app
