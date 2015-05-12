import unittest
from nct.apps.bulk_trade_loader import BulkTradeLoader, RecordProcessor
from nct.utils.alch import Session
from nct.domain.trade import Trade
from sqlalchemy.engine import create_engine
from nct.deploy.deploy import Deployer
from nct.presentation.vanilla import VanillaModel
from datetime import date

class CSVTradeLoaderTest(unittest.TestCase):
    
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session.configure( bind=engine)
    
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
        
    def test_populate_rf_from_record(self):
        Deployer.deploy()
        rec = {"Quantity": 100, "Price":123, "Action": "Buy", "Trade Date":"2015-01-01", 
                "Instrument":"BAC.N", "Fund":"Fund1", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.create_rf()
        rp.populate_rf()
        rf = rp._rf
        self.assertEquals( 100, rf.get_value('quantity' ))
        self.assertEquals( 123, rf.get_value('price' ))
        self.assertEquals( "Buy", rf.get_value('action' ))
        self.assertEquals( "BAC.N", rf.get_value('instrument' ))
        self.assertEquals( "USD", rf.get_value('currency'))
        self.assertEquals( date(2015,1,1), rf.get_value('trade_date' ))
        self.assertEquals( date(2015,1,3), rf.get_value('settle_date' ))
        self.assertEquals( "Fund1", rf.get_value('fund' ))        

    def test_populate_rf_logs_errors_setting_fields(self):
        Deployer.deploy()
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
        Deployer.deploy()
        rec = {"Quantity": 100, "Price":123, "Action": "Buy", "Trade Date":"2015-01-01", 
                "Instrument":"BAC.N", "Fund":"Fund1", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.create_rf()
        rp.populate_rf()
        rp.validate_rf()
        self.assertEquals('', rp.errors)

    def test_validate_record_when_missing_fields(self):
        Deployer.deploy()
        rec = {"Quantity": 100, "Price":123, "Action": "Buy", "Trade Date":"2015-01-01", "TradeType":"Vanilla"}
        rp = RecordProcessor(rec)
        rp.create_rf()
        rp.populate_rf()
        rp.validate_rf()
        self.assertEquals( "'Currency': 'Not set', 'Fund': 'Not set'",  rp.errors)
           
    
    def test_load_trades_basic_integration(self):
        Deployer.deploy()
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

        s = Session()
        trades = s.query(Trade).all()
        self.assertEquals( 2, len(trades) )

