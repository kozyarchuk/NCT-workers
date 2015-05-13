import unittest
from nct.apps.bulk_trade_loader import BulkTradeLoader, RecordProcessor
from nct.presentation.vanilla import VanillaModel
from tests.test_util import TestSchema

class WrappedRF:
    save_called = False
    validate_called = False
    set_value_called = False
    
    def __init__(self, wrapped):
        self.wrapped = wrapped
        
    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)
    
    def save(self):
        self.save_called = True
    def validate(self):
        self.validate_called = True
        return {}    
    def set_value(self, field, value):
        self.set_value_called = True

    @classmethod
    def get_processor(cls):
        rp = RecordProcessor({'Quantity':100, "TradeType":"Vanilla"})
        rp.create_rf()
        rp._rf = cls(rp._rf)
        return rp



class CSVTradeLoaderTest(unittest.TestCase):
    
    def setUp(self):
        TestSchema.create()
        
    def test_load_empty_trade_file_produces_empty_result(self):
        csv_items = []
        
        result = BulkTradeLoader(csv_items).load()
        self.assertEquals(0, result.total)
        self.assertEquals(0, result.loaded)
        self.assertEquals(0, result.errors)
        self.assertEquals(0, result.failed)
        self.assertEquals([], result.rejected_trades)

    def test_load_fails_if_not_able_to_determine_presentation_model(self):
        
        input_rec = dict(quantity=100, price = 123)
        csv_items = [input_rec]
        result = BulkTradeLoader(csv_items).load()
        self.assertEquals(1, result.total)
        self.assertEquals(0, result.loaded)
        self.assertEquals(1, result.errors)
        self.assertEquals(0, result.failed)
        self.assertEquals(1, len( result.rejected_trades))
        expect_rec = dict(input_rec)
        expect_rec.update({"Status":"TradeType must be specified"})
        self.assertEquals(result.rejected_trades[0], expect_rec)

    def test_create_rf_from_trade_type(self):
        rec = { "Fund":"Fund1", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.create_rf()
        self.assertEquals(VanillaModel, rp._rf.model.__class__)
        
    def test_populate_rf_maps_fields_and_records_errors(self):
        rec = {"Quantity": 'ABC', "Price":123, "Action": "Buy", "Trade Date":"2015-13-01", 
                "Instrument":"BAC.N", "Fund":"Invalid", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.create_rf()
        rp.populate_rf()
        rf = rp._rf
        self.assertEquals( None, rf.get_value('quantity' ))
        self.assertEquals( 123, rf.get_value('price' ))
        self.assertEquals( "Buy", rf.get_value('action' ))
        self.assertEquals( "BAC.N", rf.get_value('instrument' ))
        self.assertEquals( "USD", rf.get_value('currency'))
        self.assertEquals( None, rf.get_value('trade_date' ))
        self.assertEquals( None, rf.get_value('settle_date' ))
        self.assertEquals( "Invalid", rf.get_value('fund' ))        
        expect = "'Quantity': 'Invalid value >ABC< needs to be Numeric', 'Trade Date': 'Invalid value >2015-13-01< needs to be YYYY-MM-DD format'"
        self.assertEquals(expect,  rp.errors )
        

    def test_validate_record_when_all_is_good(self):
        rec = {"Quantity": 100, "Price":123, "Action": "Buy", "Trade Date":"2015-01-01", 
                "Instrument":"BAC.N", "Fund":"Fund1", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.process()
        self.assertEquals('', rp.errors)

    def test_validate_record_when_missing_fields(self):
        rec = {"Quantity": 100, "Price":123, "Action": "Buy", "Trade Date":"2015-01-01", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.process()
        self.assertEquals( "'Currency': 'Not set', 'Fund': 'Not set'",  rp.errors)

    def test_create_rf_when_trade_type_is_missing(self):
        rp = RecordProcessor({})
        rp.create_rf()
        self.assertEquals("TradeType must be specified", rp.errors)
        self.assertEquals(None, rp._rf )

    def test_create_rf_when_trade_type_is_not_set(self):
        rp = RecordProcessor({'TradeType':""})
        rp.create_rf()
        self.assertEquals("TradeType must be specified", rp.errors)
        self.assertEquals(None, rp._rf)
                                  
    def test_save_does_not_call_save_when_there_are_errors(self):
        rp = WrappedRF.get_processor()
        rp.errors = "Errors"
        rp.save()
        self.assertFalse(rp._rf.save_called)
    
    def test_save_call_save_when_no_errors(self):
        rp = WrappedRF.get_processor()
        rp.save()
        self.assertTrue(rp._rf.save_called)

    def test_validate_does_not_call_validate_when_there_are_errors(self):
        rp = WrappedRF.get_processor()
        rp.errors = "Errors"
        rp.validate_rf()
        self.assertFalse(rp._rf.validate_called)
    
    def test_validate_call_validate_when_no_errors(self):
        rp = WrappedRF.get_processor()
        rp.validate_rf()
        self.assertTrue(rp._rf.validate_called)

    def test_setvalue_does_not_call_setvalue_when_there_are_errors(self):
        rp = WrappedRF.get_processor()
        rp.errors = "Errors"
        rp.populate_rf()
        self.assertFalse(rp._rf.set_value_called)
    
    def test_setvalue_call_setvalue_when_no_errors(self):
        rp = WrappedRF.get_processor()
        rp.populate_rf()
        self.assertTrue(rp._rf.set_value_called)
        
    def test_load_trades_basic_integration(self):
        rec1 = {"Quantity": 100, "Price":123, "Action": "Buy", "Trade Date":"2015-01-01", 
                "Instrument":"BAC.N", "Fund":"Fund1", "TradeType":"Vanilla"}
        
        rec2 = {"Quantity": 200, "Price":23, "Action": "Buy", "Trade Date":"2015-01-01", 
                "Instrument":"BAC.N", "Fund":"Fund1", "TradeType":"Vanilla"}
        rec3 = {"Quantity": 200, "Price":23, "Action": "Buy", "Trade Date":"", 
                "Instrument":"BAC.N", "Fund":"Fund1", "TradeType":"Vanilla"}
        rec4 = {"Quantity": 200, "Price":23, "Action": "Buy", "Trade Date":"2015-11-01", 
                "Instrument":"BAC.N", "Fund":"Invalid", "TradeType":"Vanilla"}

        csv_items = [rec1, rec2, rec3, rec4]
        result = BulkTradeLoader(csv_items).load()
        self.assertEquals(4, result.total)
        self.assertEquals(2, result.loaded)
        self.assertEquals(2, result.errors)
        self.assertEquals(0, result.failed)
        self.assertEquals(2, len( result.rejected_trades))
        expect_rec = dict(rec3)
        expect_rec.update({"Status":"'Settle Date': 'Not set', 'Trade Date': 'Not set'"})
        self.assertEquals(result.rejected_trades[0], expect_rec)

