import unittest
from nct.presentation.vanilla import VanillaModel
from nct.utils.reactive.framework import ReactiveFramework
from nct.utils.alch import Session
from nct.domain.trade import Trade
from datetime import date
from nct.domain.portfolio import Portfolio
from tests.test_util import TestSchema, get_next_id
from nct.utils.reactive.bound_field import BoundField
from nct.utils.reactive.field import Field

class StubInner:
    name = 'a name'
    an_attr = 'a value'

def finder(value):
    return "Found {}".format(value)

class StubObj:
    field1 = StubInner()
    field2 = 'Some other value'


class VanillaModelTest(unittest.TestCase):
    
    def setUp(self):
        TestSchema.create()

    def book_a_trade(self):
        rf = ReactiveFramework(VanillaModel())
        rf.set_value('quantity', 100)
        rf.set_value('price', 600)
        rf.set_value('action', "Buy")
        rf.set_value('instrument', "GOOGL.O")
        rf.set_value('trade_date', date(2015, 5, 5))
        rf.set_value('fund', "Fund1")
        rf.set_value('trader', "Trader1")
        rf.set_value('analyst', "Analyst1")
        rf.set_value('broker', "Broker1")
        rf.set_value('clearer', "Clearer1")
        rf.set_value('sector', "sec1")
        rf.set_value('strategy', "strat1")
        rf.set_value('trade_id', "ZZ{}".format(get_next_id()))
        self.assertEquals({},  rf.validate() )
        trade_id = rf.save()
        return trade_id
         
    def test_creating_vanilla_model_creates_empty_trade(self):
        m = VanillaModel()
        trade = m.get_domain_object(m.TRADE)
        self.assertEquals(None, trade.quantity)
        p = m.get_domain_object(m.PORTFOLIO)
        self.assertEquals(None, p.fund)
 
    def test_calc_settle_date_basic(self):
        rf = ReactiveFramework(VanillaModel())
        rf.set_value('trade_date', date(2015,5,6))
        self.assertEquals(date(2015,5,8), rf.get_value('settle_date'))
         
    def test_map_object_value_basic_to(self):

        so = StubObj()
        bf = BoundField(Field("field1", str), None)    
        bf.set_value('some value')
        
        model = VanillaModel()
        model._map_object_value(so, bf, bf.TO, finder)
        self.assertEquals(so.field1, 'Found some value')

    def test_map_object_value_to_when_none(self):

        so = StubObj()
        bf = BoundField(Field("field2", str), None)    
        bf.set_value(None)
        
        model = VanillaModel()
        model._map_object_value(so, bf, bf.TO, finder)
        self.assertEquals(so.field2, None)

    def test_map_object_value_basic_from(self):

        so = StubObj()
        bf = BoundField(Field("field1", str), None)    
        
        model = VanillaModel()
        actual = model._map_object_value(so, bf, bf.FROM, finder)
        expect = "a name"
        self.assertEquals(expect, actual )

    def test_map_object_value_from_when_none(self):

        so = StubObj()
        bf = BoundField(Field("field1", str), None)    
        so.field1 = None
        
        model = VanillaModel()
        actual = model._map_object_value(so, bf, bf.FROM, finder)
        expect = None
        self.assertEquals(expect, actual )
         
    def test_integration(self):
        s = Session()
        s.query(Trade).delete()
        s.query(Portfolio).delete()
        trade_id = self.book_a_trade()
        trades = s.query(Trade).all()
        self.assertEquals( 1, len(trades) )
        self.assertEquals( trade_id, trades[0].trade_id)
        self.assertEquals( 100, trades[0].quantity )
        self.assertEquals( 600, trades[0].price )
        self.assertEquals( "Buy", trades[0].action.value )
        self.assertEquals( "GOOGL.O", trades[0].instrument.name )
        self.assertEquals( "USD", trades[0].currency.name )
        self.assertEquals( date(2015,5,5), trades[0].trade_date )
        self.assertEquals( date(2015,5,7), trades[0].settle_date )
        self.assertEquals( "Fund1", trades[0].portfolio.fund.name )   

        s = Session()
        ports = s.query(Portfolio).all()
        self.assertEquals( 1, len(ports) )
        self.assertEquals( 'Fund1', ports[0].fund.name )
        self.assertEquals( 'Trader1', ports[0].trader.name )
        self.assertEquals( 'Analyst1', ports[0].analyst.name )
        self.assertEquals( 'Broker1', ports[0].broker.name )
        self.assertEquals( 'Clearer1', ports[0].clearer.name )
        self.assertEquals( 'sec1', ports[0].sector )
        self.assertEquals( 'strat1', ports[0].strategy )

        rf = ReactiveFramework(VanillaModel())
        rf.load(trade_id)
        self.assertEquals( 100, rf.get_value('quantity' ))
        self.assertEquals( 600, rf.get_value('price' ))
        self.assertEquals( "Buy", rf.get_value('action' ))
        self.assertEquals( "GOOGL.O", rf.get_value('instrument' ))
        self.assertEquals( "USD", rf.get_value('currency'))
        self.assertEquals( date(2015,5,5), rf.get_value('trade_date' ))
        self.assertEquals( date(2015,5,7), rf.get_value('settle_date' ))
        self.assertEquals( "Fund1", rf.get_value('fund' ))
        self.assertEquals( "Trader1", rf.get_value('trader' ))
        self.assertEquals( "Analyst1", rf.get_value('analyst' ))
        self.assertEquals( "Broker1", rf.get_value('broker' ))
        self.assertEquals( "Clearer1", rf.get_value('clearer' ))
        self.assertEquals( "sec1", rf.get_value('sector' ))
        self.assertEquals( "strat1", rf.get_value('strategy' ))
        
        
        rf.set_value( 'quantity', -140)
        rf.set_value( 'price', 600)
        rf.set_value( 'action', "Sell")
        rf.set_value( 'instrument', "GOOGL.O")
        rf.set_value( 'trade_date', date(2015,5,5))
        rf.set_value( 'fund', "Fund2")
        self.assertEquals({}, rf.validate())
        rf.save()
 
        s = Session()
        trades = s.query(Trade).all()
        self.assertEquals( 1, len(trades) )
        self.assertEquals( -140, trades[0].quantity )
        self.assertEquals( 600, trades[0].price )
        self.assertEquals( "Sell", trades[0].action.value )
        self.assertEquals( "GOOGL.O", trades[0].instrument.name )
        self.assertEquals( "USD", trades[0].currency.name )
        self.assertEquals( date(2015,5,5), trades[0].trade_date )
        self.assertEquals( date(2015,5,7), trades[0].settle_date )
        self.assertEquals( "Fund2", trades[0].portfolio.fund.name )
 
        rf.delete()
        trades = s.query(Trade).all()
        self.assertEquals( 0, len(trades) )
    
    def test_saving_two_trades_with_same_fund_does_not_create_two_portfolios(self):
        s = Session()
        s.query(Trade).delete()
        s.query(Portfolio).delete()
        self.book_a_trade()
        self.book_a_trade()
        trades = s.query(Trade).all()
        self.assertEquals( 2, len(trades) )
        ports = s.query(Portfolio).all()
        self.assertEquals( 1, len(ports) )

    def test_load_missing_trade(self):
        rf = ReactiveFramework(VanillaModel())
        self.assertEquals(None, rf.load('ABC123'))

    def test_load_existing_trade(self):
        trade_id = self.book_a_trade()
        rf = ReactiveFramework(VanillaModel())
        self.assertEquals(trade_id, rf.load(trade_id))


