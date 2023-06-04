import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    FRAMEWORKS = ["bootstrap", "bulma"]
    FRAMEWORK = os.environ.get("FRAMEWORK") or FRAMEWORKS[0]
    OUTPUT = os.environ.get("OUTPUT") or "local"  # local or docker
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "really-hard-to-guess-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
