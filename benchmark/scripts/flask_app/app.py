#!/usr/bin/env python
from flask import Flask
from .config import Config

# from .results import results
from .main import main


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    # app.register_blueprint(results)
    app.config.from_object(Config)
    app.jinja_env.auto_reload = True
    return app
