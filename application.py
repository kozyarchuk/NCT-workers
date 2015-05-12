import flask
import logging
from flask.templating import render_template
from nct.utils.db_logger import DBLogger
from flask import request


# create logger
logger = logging.getLogger('NCT Workers')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
handler = DBLogger()
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)

application = flask.Flask(__name__)

@application.route('/',methods=['POST'])
@application.route('/service-request',methods=['POST'])
def hello_world():
    logger.info("REQUEST>%s<" % request.__dict__)
    application.logger.warning('The request is in')
    return "Request handled."

if __name__ == '__main__':
    application.debug=True
    application.run(host='0.0.0.0')
