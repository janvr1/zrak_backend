import os
import subprocess
from flask import Flask
from flask_cors import CORS
from . import db, api, auth, manage


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'zrak_db.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def greeting():
        return "Watcha doin here?"

    app.jinja_env.globals.update(uptime=uptime)

    db.init_app(app)
    app.register_blueprint(api.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(manage.bp)
    return app


def uptime():
    return subprocess.run(['uptime'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
