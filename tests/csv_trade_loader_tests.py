import unittest
from nct.apps.csv_trade_loader import CSVTradeLoader
import os
import tempfile
from nct.utils.alch import Session
from nct.domain.trade import Trade
from nct.deploy.deploy import Deployer

class CSVTradeLoaderTest(unittest.TestCase):
    
    def test_error_file(self):
        loader = CSVTradeLoader("file_root")
        self.assertEquals('file_root_errors.csv', loader.error_file)

    def test_trade_file(self):
        loader = CSVTradeLoader("file_root")
        self.assertEquals('file_root.csv', loader.trade_file)

    def test_load_trade_file(self):
        loader = CSVTradeLoader("trade_file", source = os.path.dirname(__file__))
        fields, trades = loader.load_trade_file()
        expect = ['Quantity', 'Price', 'Action', 'Trade Date', 'Instrument', 'Fund', 'TradeType']
        self.assertEquals( expect, fields )
        self.assertEquals( 2, len(trades))
        expect = {'Action': 'Buy', 'Fund': 'Fund1',
                  'Instrument': 'BAC.N', 'Price': '22',
                  'Quantity': '200', 'Trade Date':  '2015-03-03',
                  'TradeType': 'Vanilla'}
        
        self.assertEquals(expect, trades[0])

    def test_write_csv(self):
        loader = CSVTradeLoader("some_csv")
        headers = ['F1', 'F2']
        data = [{'F1':'V1'}, {'F1':'V1','F2':'V2'}]
        loader.write_csv('some_csv.csv', headers, data)
        with open(os.path.join( tempfile.gettempdir(),'some_csv.csv'),'r') as f:
            expect = 'F1,F2\n\nV1,\n\nV1,V2\n\n'
            self.assertEquals(expect, f.read())
            
    def test_integration(self):
        Deployer.deploy()
        loader = CSVTradeLoader("trade_file", source = os.path.dirname(__file__))
        loader.run()
        with open(os.path.join( tempfile.gettempdir(),loader.error_file),'r') as f:
            expect = 'Quantity,Price,Action,Trade Date,Instrument,Fund,TradeType,Status\n\n'
            self.assertEquals(expect, f.read())

        s = Session()
        trades = s.query(Trade).all()
        self.assertEquals( 2, len(trades) )



            

            