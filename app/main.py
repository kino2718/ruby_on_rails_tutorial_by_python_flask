from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    @app.route('/')
    def application_hello():
        from controllers import application_controller
        return application_controller.hello()

    from controllers import static_pages_controller
    app.register_blueprint(static_pages_controller.bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
