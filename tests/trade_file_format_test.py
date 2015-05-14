import unittest
from nct.utils.bulk_upload_format import BulkUploadFormat
from nct.utils.reactive.reactive_model import ReactiveModel
from nct.utils.reactive.field import Field
from decimal import Decimal
import tempfile
import os
import csv

class FirstModel(ReactiveModel):
    FIELD_DEPENDS = {"quantity":[]}
class SecondModel(ReactiveModel):
    FIELD_DEPENDS = {"other":[]}

class BulkUploadFormatTest(unittest.TestCase):
    
    def test_format_data_table_default(self):
        data = BulkUploadFormat.get_data_table(fields = [], models = [])
        self.assertEquals(2, len(data))
        self.assertEquals(["Msg Type", "TradeType"], [r['FieldName'] for r in data ])
        
    def test_single_field_no_models(self):

        data = BulkUploadFormat.get_data_table(fields = [("Quantity", "quantity")], models = [])
        expect = {"FieldName":'Quantity', "Format":"Numeric","Validations":"must_be_provided", "Calculations":""}
        self.assertEquals(3, len(data))
        self.assertEquals(expect, data[2])
        
    def test_map_field_maps_to_models(self):

        field = Field(name = 'quantity', datatype = Decimal)
        actual = BulkUploadFormat.map_one_field("Quantity", field, models = [FirstModel, SecondModel])
        self.assertEquals("X", actual["First"])
        self.assertEquals("", actual["Second"])
    
    def test_format_for_trade_type(self):
        actual = BulkUploadFormat.format_trade_type(models = [FirstModel, SecondModel])
        self.assertEquals("TradeType", actual["FieldName"])
        self.assertEquals("Model Name", actual["Format"])
        self.assertEquals("required", actual["Validations"])
        self.assertEquals("", actual["Calculations"])
        self.assertEquals("X", actual["First"])
        self.assertEquals("X", actual["Second"])
        
    def test_format_for_msg_type(self):
        actual = BulkUploadFormat.format_msg_type(models = [FirstModel, SecondModel])
        self.assertEquals("Msg Type", actual["FieldName"])
        self.assertEquals("New,Edit,Cancel", actual["Format"])
        self.assertEquals("required", actual["Validations"])
        self.assertEquals("", actual["Calculations"])
        self.assertEquals("X", actual["First"])
        self.assertEquals("X", actual["Second"])
        
    def test_get_headers(self):
        actual = BulkUploadFormat.get_headers(models = [FirstModel, SecondModel])
        expect = ['FieldName', "Format", "Validations", "Calculations", "First", "Second"]
        self.assertEquals(expect, actual)
        data = BulkUploadFormat.get_data_table(fields = [], models = [FirstModel, SecondModel])
        self.assertEquals(sorted(expect), sorted(data[0].keys()))

    def test_trade_file_format_as_csv(self):
        file_name = os.path.join(tempfile.gettempdir(),"TradeFileFormat.csv")
        BulkUploadFormat.build_csv(file_name)
        expect1 = ['FieldName', 'Format', 'Validations', 'Calculations', 'Vanilla']
        expect2 = ['Msg Type', 'New,Edit,Cancel', 'required', '', 'X']
        
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            records  = [r for r in reader]
            self.assertEquals(expect1, records[0])
            self.assertEquals(expect2, records[1])
