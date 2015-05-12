import flask
import logging
from nct.utils.db_logger import DBLogger
from flask import request
import boto
from nct.utils.s3_message import S3Message
import tempfile

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
#         return  self.conn.get_bucket(self.BUCKET)
# 
#     @property
#     def conn(self):
#         if not self._conn:
#             self._
#         return self._conn
# #     @property


@application.route('/',methods=['POST'])
@application.route('/service-request',methods=['POST'])
def process_trade_file():
    try:
        for record in S3Message.parse(request.json):
            bucket = conn.get_bucket(record.bucket)
            trade_file_key = bucket.get_key(record.file_name)
            trade_file_url = trade_file_key.generate_url(0, query_auth=False, force_http=True)
            logger.info("TF URL: %s" % trade_file_url )
            f, file_name = tempfile.mkstemp(".csv")
            f.close()
            urlretrieve(trade_file_url, file_name)
            logger.info("Uploading Trade File: %s" % file_name )
            loader = CSVTradeLoader.create_from_path(file_name)
            loader.run()
            logger.info("File uploaded")
    except Exception:
        logger.exception("Process Trade File Failed")
        
    application.logger.warning('The request is in')
    return "Request handled."

if __name__ == '__main__':
    application.debug=True
    application.run(host='0.0.0.0')
