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

    @app.after_request
    def add_default_headers(resp):
        resp.headers['X-XSS-Protection'] = '1; mode=block'
        resp.headers['X-Frame-Options'] = 'DENY'
        return resp

    @app.context_processor
    def define_template_functions():
        base_title = 'Ruby on Rails Tutorial Sample App'
        def full_title(page_title = ''):
            if not page_title:
                return base_title
            else:
                return f'{page_title} | {base_title}'
        return dict(full_title=full_title)
    return app
