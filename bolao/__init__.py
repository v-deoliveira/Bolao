import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

def create_app(test_config=None):
    # create and config app
    app = Flask(__name__, instance_relative_config=True)
    csrf = CSRFProtect(app)
    app.config.from_mapping(
        SECRET_KEY='dev' ,
        DATABASE=os.path.join(app.instance_path, 'bolao.sqlite'),
    )

    if test_config is None:
        # load the instance config, if exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import admin_matches
    app.register_blueprint(admin_matches.bp)

    from . import admin_teams
    app.register_blueprint(admin_teams.bp)

    from . import admin_tournaments
    app.register_blueprint(admin_tournaments.bp)

    from . import predictions
    app.register_blueprint(predictions.bp)

    from . import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')

    @app.route('/hello')
    def hello():
        return 'hello, world!'
    

    return app
