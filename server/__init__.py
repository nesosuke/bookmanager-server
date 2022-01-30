import os
from flask import Flask, render_template


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

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import record
    app.register_blueprint(record.bp)
    # app.add_url_rule('/', endpoint='index')

    from . import book
    app.register_blueprint(book.bp)

    @app.route('/')
    def toppage():
        return render_template('index.html')

    return app
