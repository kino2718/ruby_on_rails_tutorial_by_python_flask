from flask import Flask
from controllers import application_controller
from controllers import static_pages_controller

app = Flask(__name__)

@app.route('/')
def application_hello():
    return application_controller.hello()

@app.route('/static_pages/home')
def static_pages_home():
    return static_pages_controller.home()

@app.route('/static_pages/help')
def static_pages_help():
    return static_pages_controller.help()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
