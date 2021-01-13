from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # register static_pages blueprint
    from .controllers import static_pages_controller
    app.register_blueprint(static_pages_controller.bp)

    # register users blueprint
    from .controllers import users_controller
    app.register_blueprint(users_controller.bp)
    # map '/signup' to '/users/new'
    app.add_url_rule('/signup', endpoint='users.new')

    # register sessions blueprint
    from .controllers import sessions_controller
    app.register_blueprint(sessions_controller.bp)

    # register account_activations blueprint
    from .controllers import account_activations_controller
    app.register_blueprint(account_activations_controller.bp)

    @app.after_request
    def add_default_headers(resp):
        resp.headers['X-XSS-Protection'] = '1; mode=block'
        resp.headers['X-Frame-Options'] = 'DENY'
        return resp

    @app.context_processor
    def define_template_functions():
        from .helpers import application_helper, users_helper, sessions_helper
        app_helper_functions = application_helper.template_functions()
        users_helper_functions = users_helper.template_functions()
        sessions_helper_functions = sessions_helper.template_functions()

        helpers = {}
        helpers.update(**app_helper_functions, **users_helper_functions,
                       **sessions_helper_functions)
        return helpers
    return app
