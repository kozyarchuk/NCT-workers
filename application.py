import flask
from nct.utils.db_logger import DBLogger
from flask import request
import boto
from nct.utils.s3_message import S3Message
import sys, os, tempfile, logging
from nct.apps.csv_trade_loader import CSVTradeLoader

if sys.version_info >= (3,):
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve
    

# create logger
logger = logging.getLogger('NCT Workers')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
handler = DBLogger()
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)

application = flask.Flask(__name__)
conn = boto.connect_s3()

@application.route('/',methods=['POST'])
@application.route('/service-request',methods=['POST'])
def process_trade_file():
    try:
        for record in S3Message.parse(request.json):
            logger.info( "Processing of {} started".format(record.file_name))
            result = record.process(conn) 
            logger.info( "Processing complete with {}".format( result ))
    except Exception:
        logger.exception("Process Trade File Failed")
    return "Request handled."

if __name__ == '__main__':
    application.debug=True
    application.run(host='0.0.0.0')
