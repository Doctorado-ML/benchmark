#!/usr/bin/env python
from benchmark.Arguments import EnvData
from flask import Flask
from .main import main

FRAMEWORK = "framework"
FRAMEWORKS = "frameworks"
TEST = "test"


def create_app():
    app = Flask(__name__)
    config = EnvData().load()
    app.register_blueprint(main)
    app.config[FRAMEWORK] = config[FRAMEWORK]
    app.config[FRAMEWORKS] = ["bootstrap", "bulma"]
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    return app
