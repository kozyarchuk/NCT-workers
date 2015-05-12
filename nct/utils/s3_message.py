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
        