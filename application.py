import flask
from flask.templating import render_template

application = flask.Flask(__name__)

@application.route('/')
@application.route('/service-request')
def hello_world():
    application.logger.warning('The request is in')
    return "Request handled."

if __name__ == '__main__':
    application.debug=True
    application.run(host='0.0.0.0')
