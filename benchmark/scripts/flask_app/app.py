#!/usr/bin/env python
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from .config import Config
from .models import User, db

# from .results import results
from .main import main

bootstrap = Bootstrap5()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))


def create_app():
    # db.create_all()
    app = Flask(__name__)
    bootstrap.init_app(app)
    # app.register_blueprint(results)
    app.config.from_object(Config)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    app.jinja_env.auto_reload = True
    app.register_blueprint(main)
    return app
