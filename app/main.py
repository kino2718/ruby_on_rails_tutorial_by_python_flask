from flask import Flask
import controllers.application_controller

app = Flask(__name__)

@app.route('/')
def application_hello():
    return controllers.application_controller.hello()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
