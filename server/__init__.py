import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True,
                static_url_path='/static', template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'bookmeter.sqlite'),
    )
    if test_config is None:
        # Not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # already exists

    from . import Db
    Db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    return app
