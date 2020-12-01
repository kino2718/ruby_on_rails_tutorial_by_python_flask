from flask import Flask
import logging

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.route('/')
    def application_hello():
        from .controllers import application_controller
        return application_controller.hello()

    from .controllers import static_pages_controller
    app.register_blueprint(static_pages_controller.bp)
    return app
