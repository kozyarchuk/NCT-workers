import unittest
from nct.presentation.vanilla import VanillaModel
from nct.utils.reactive.framework import ReactiveFramework
from nct.utils.alch import Session
from nct.domain.trade import Trade
from datetime import date
from nct.deploy.deploy import Deployer
from sqlalchemy.engine import create_engine

class VanillaModelTest(unittest.TestCase):
    
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session.configure( bind=engine)
        
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
        
    def test_create_and_save_basic(self):
        Deployer.deploy()
        rf = ReactiveFramework(VanillaModel())
        rf.set_value( 'quantity', 100)
        rf.set_value( 'price', 600)
        rf.set_value( 'action', "Buy")
        rf.set_value( 'instrument', "GOOGL.O")
        rf.set_value( 'trade_date', date(2015,5,5))
        rf.set_value( 'fund', "Fund1")
        rf.save()
        s = Session()
        trades = s.query(Trade).all()
        self.assertEquals( 1, len(trades) )
        self.assertEquals( 100, trades[0].quantity )
        self.assertEquals( 600, trades[0].price )
        self.assertEquals( "Buy", trades[0].action.value )
        self.assertEquals( "GOOGL.O", trades[0].instrument.name )
        self.assertEquals( "USD", trades[0].currency.name )
        self.assertEquals( date(2015,5,5), trades[0].trade_date )
        self.assertEquals( date(2015,5,7), trades[0].settle_date )
        self.assertEquals( "Fund1", trades[0].portfolio.fund.name )

    