from nct.deploy.deploy import  Deployer
from nct.utils.bulk_upload_format import BulkUploadFormat

if __name__ == '__main__':
    print ( "Install Starting" )
    print ( "Updating DB Configuration" )
    Deployer().deploy()
    print ( "Updating Bulk Upload Format document" )
    BulkUploadFormat.deploy_to_s3()
    print ( "Install Complete" )
