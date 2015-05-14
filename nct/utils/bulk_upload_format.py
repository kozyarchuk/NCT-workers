from nct.utils.reactive.field_factory import FieldFactory
from nct.apps.bulk_trade_loader import RecordProcessor
from nct.apps.csv_trade_loader import CSVTradeLoader
from nct.utils.reactive.bound_field import datatype_format
from nct.utils.config import Config


def format_value(value):
    if value is None:
        return ""
    return value

class BulkUploadFormat:
    FIELD_NAME ="FieldName"
    DATA_TYPE ="Format"
    VALIDATIONS ="Validations"
    CALCS ="Calculations"

    @classmethod
    def format_trade_type(cls, models):
        ret = {cls.FIELD_NAME:RecordProcessor.TRADE_TYPE, 
                cls.DATA_TYPE:"Model Name", 
                cls.VALIDATIONS:"required", 
                cls.CALCS:""}
        for model in models:
            ret[model.model_name()] = "X"
        return ret

    @classmethod
    def format_msg_type(cls, models):
        ret = {cls.FIELD_NAME:RecordProcessor.MSG_TYPE, 
                cls.DATA_TYPE:",".join(RecordProcessor.MSG_TYPE_VALUES), 
                cls.VALIDATIONS:"required", 
                cls.CALCS:""}
        for model in models:
            ret[model.model_name()] = "X"
        return ret

    
    @classmethod
    def map_one_field(cls, external_field, field, models):
        ret = {cls.FIELD_NAME:external_field, 
                cls.DATA_TYPE:datatype_format(field.datatype), 
                cls.VALIDATIONS:format_value(field.validation_method), 
                cls.CALCS:format_value(field.calculation_method)}
        for model in models:
            ret[model.model_name()] = "X" if field.name in model.FIELD_DEPENDS else ""
            
        return ret
    
    @classmethod
    def get_data_table(cls, fields, models):
        ret = []
        ret.append(cls.format_msg_type(models))
        ret.append(cls.format_trade_type(models))
        for external_field, internal_field in fields:
            field = FieldFactory.get_field(internal_field)
            ret.append(cls.map_one_field(external_field, field, models))
        return ret
    
    @classmethod
    def get_headers(cls, models):
        ret = [cls.FIELD_NAME, cls.DATA_TYPE, cls.VALIDATIONS, cls.CALCS]
        for model in models:
            ret.append( model.model_name())
        return ret
    
    @classmethod
    def build_csv(cls, file_name):
        models = RecordProcessor.model_list()
        fields = RecordProcessor.FIELD_MAP
        records = cls.get_data_table(fields, models)
        CSVTradeLoader.write_csv(file_name, cls.get_headers(models), records)
            
    @classmethod
    def deploy_to_s3(cls):
        import boto
        import os
        import tempfile
        
        file_path = os.path.join(tempfile.gettempdir(),Config.BULK_UPLOAD_FORMAT)
        cls.build_csv(file_path)
        conn = boto.connect_s3()
        bucket = conn.get_bucket(Config.BUCKET)
        key = bucket.new_key(Config.BULK_UPLOAD_FORMAT)
        key.set_contents_from_filename(file_path)
          
