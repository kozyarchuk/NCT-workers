import flask
from flask.templating import render_template

app = flask.Flask(__name__)

@app.route('/')
@app.route('/service-request')
def hello_world():
    app.logger.warning('The request is in')
    return "Request handled."

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')
