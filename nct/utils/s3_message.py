import os
import tempfile
from nct.apps.csv_trade_loader import CSVTradeLoader

class S3Message:
    
    def __init__(self, bucket, file_name):
        self.bucket = bucket
        self.file_name = file_name
    
    @classmethod
    def parse(self, msg_dict):
        recs = []
        for record in msg_dict['Records']:
            recs.append( S3Message(bucket     = record['s3']['bucket']['name'],
                             file_name  = record['s3']['object']['key']) )
        return recs
        
    def process(self, conn):
        bucket = conn.get_bucket(self.bucket)
        trade_file_key = bucket.get_key(self.file_name)

        if str(trade_file_key.get_metadata('user_upload')).lower() !='true':
            return ("Skipping {}. Not user uploaded file".format(self.file_name))
        
        trade_file = os.path.join(tempfile.gettempdir(),self.file_name)
        trade_file_key.get_contents_to_filename(trade_file)
        
        loader = CSVTradeLoader.create_from_path(trade_file)
        loader.run()

        error_file_key = bucket.new_key(loader.error_file)
        error_file_key.set_contents_from_filename(loader.error_filepath)

        os.remove(trade_file)
        os.remove(loader.error_filepath)
        return ("Trade file processed. {} filed produced".format( loader.error_file ))
                
