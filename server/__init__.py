import os
from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True,
                static_url_path='/static', template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'bookmeter.sqlite'),
    )
    CORS(app)
    if test_config is None:
        # Not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # already exists

    from . import db
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    from . import webview
    app.register_blueprint(webview.bp)

    return app
