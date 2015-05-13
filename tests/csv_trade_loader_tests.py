import os
import sys
import tempfile
import unittest
from nct.apps.csv_trade_loader import CSVTradeLoader, CSVLoaderError
from tests.test_util import TestSchema

if sys.version_info[:2] == (2, 7):
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp

class CSVTradeLoaderTest(unittest.TestCase):
    
    def setUp(self):
        TestSchema.create()
    
    def test_error_file(self):
        loader = CSVTradeLoader("file_root", output= '/foo/bar')
        self.assertEquals(r'file_root_errors.csv', loader.error_file)
    
    def test_error_filepath(self):
        loader = CSVTradeLoader("file_root", output= '/foo/bar')
        self.assertEquals(os.path.join('/foo/bar', 'file_root_errors.csv'), loader.error_filepath)

    def test_trade_file(self):
        loader = CSVTradeLoader("file_root")
        self.assertEquals('file_root.csv', loader.trade_file)

    def test_load_trade_file(self):
        loader = CSVTradeLoader("trade_file", source = os.path.dirname(__file__))
        fields, trades = loader.load_trade_file()
        expect = ['Quantity', 'Price', 'Action', 'Trade Date', 'Instrument', 'Fund', 'TradeType', "Trade ID"]
        self.assertEquals( expect, fields )
        self.assertEquals( 3, len(trades))
        expect = {'Action': 'Buy', 'Fund': 'Fund1',
                  'Instrument': 'BAC.N', 'Price': '22',
                  'Quantity': '200', 'Trade Date':  '2015-03-03',
                  'TradeType': 'Vanilla','Trade ID': '123',}
        
        self.assertEquals(expect, trades[0])

    def test_write_csv(self):
        loader = CSVTradeLoader("some_csv")
        headers = ['F1', 'F2']
        data = [{'F1':'V1'}, {'F1':'V1','F2':'V2'}]
        csv_file = os.path.join( tempfile.gettempdir(),'some_csv.csv')
        loader.write_csv(csv_file, headers, data)
        with open(csv_file,'r') as f:
            expect = 'F1,F2\n\nV1,\n\nV1,V2\n'
            self.assertEquals(expect.replace("\n","").replace("\r",""), f.read().replace("\n","").replace("\r",""))
            
    def test_integration(self):
        loader = CSVTradeLoader("trade_file", source = os.path.dirname(__file__))
        loader.run()
        with open(os.path.join( tempfile.gettempdir(),loader.error_file),'r') as f:
            expect = 'Quantity,Price,Action,Trade Date,Instrument,Fund,TradeType,Trade ID,Status\n\n'
            expect += "333,112,Buy,2015-03-03,BAC.N,Fund1,,,TradeType must be specified"
            self.assertEquals(expect.replace("\n", "").replace("\r",""), f.read().replace("\n", "").replace("\r",""))

    def test_create_from_path(self):
        file_name = '/foo/bar/test.csv'
        loader = CSVTradeLoader.create_from_path(file_name)
        self.assertEquals('test', loader.file_root)
        self.assertEquals('/foo/bar', loader.source)
        self.assertEquals('/foo/bar', loader.output)

    def test_create_from_path_only_supports_csv(self):
        self.assertRaisesRegex(CSVLoaderError,'Invalid extension', CSVTradeLoader.create_from_path, '/foo/bar/test.bad' )
        

            

            