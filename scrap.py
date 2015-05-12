import boto
import tempfile
import os
conn = boto.connect_s3()
BUCKET_NAME = 'nct-test-data'
FILE_NAME = 'trade_file.csv'
def upload_file():
    bucket = conn.get_bucket( BUCKET_NAME )
    file_name = r'C:\Users\maksim\git\NCT-workers\tests\trade_file.csv'
    
    key = bucket.new_key(FILE_NAME)
    key.set_metadata('user_upload', True)
    with open(file_name, 'r') as f:
        key.set_contents_from_string(f.read())
    print ('done')
    
def download_file():
    bucket = conn.get_bucket( BUCKET_NAME )
    trade_file_key = bucket.get_key(FILE_NAME)
    fd, tmp_name = tempfile.mkstemp(".csv")
    trade_file_key.get_contents_to_filename(tmp_name)
    user_uploaded = trade_file_key.get_metadata('user_upload' )

    return 

    print ("saved content {}".format(tmp_name))
    print('user_upload: {}({})'.format( trade_file_key.get_metadata('user_upload' ),
                                     type(trade_file_key.get_metadata('user_upload' ) ) ))
    print('other: {}({})'.format( trade_file_key.get_metadata('other' ),
                                     type(trade_file_key.get_metadata('other' ) ) ))
    os.close(fd)
#     os.remove(tmp_name)

upload_file()
download_file()