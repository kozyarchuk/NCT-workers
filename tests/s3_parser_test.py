import unittest
from nct.utils.s3_message import S3Message

class S3ParserTest(unittest.TestCase):

    def test_parse_message(self):
        msg_dict = {u'Records': [
                    {u'eventVersion': u'2.0', u'eventTime': u'2015-05-12T13:45:10.580Z', 
                     u'requestParameters': {u'sourceIPAddress': u'52.4.162.43'}, 
                     u's3': {u'configurationId': u'NCTDataFileUpload', 
                                 u'object': {u'eTag': u'36818b4b9da36a9407b2bbfa63683c3b', u'key': u'trade_file.1431438310.54..csv', u'size': 148}, 
                                 u'bucket': {u'arn': u'arn:aws:s3:::nct-data', u'name': u'nct-data', u'ownerIdentity': {u'principalId': u'A299EFWN7PKFD9'}}, 
                                 u's3SchemaVersion': u'1.0'
                             }, 
                     u'responseElements': {u'x-amz-id-2': u'fKQctHvdRuIVApMnNQOm/ba6lks1iWHPXH0tAMCdzwuEmoR4XHCDkGOxlbCv9WawmgfEwh0fjEk=', u'x-amz-request-id': u'966C4B5E45B0A5EA'}, 
                     u'awsRegion': u'us-east-1', u'eventName': u'ObjectCreated:Put', 
                     u'userIdentity': {u'principalId': u'AWS:AROAI27NRLLHRFJCMXPZA:i-2ebdfbd3'}, 
                     u'eventSource': u'aws:s3'}]}
        
        recs = S3Message.parse(msg_dict)
        self.assertEquals(1, len(recs))
        msg = recs[0]
        self.assertEquals('nct-data', msg.bucket)
        self.assertEquals('trade_file.1431438310.54..csv', msg.file_name)        