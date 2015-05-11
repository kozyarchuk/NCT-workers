import unittest
from nct.presentation.vanilla import VanillaModel
from nct.utils.reactive.framework import ReactiveFramework
from nct.utils.alch import Session
from nct.domain.trade import Trade
from datetime import date
from nct.deploy.deploy import Deployer
from sqlalchemy.engine import create_engine
from nct.domain.portfolio import Portfolio

class VanillaModelTest(unittest.TestCase):
    
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session.configure( bind=engine)

    def book_a_trade(self):
        rf = ReactiveFramework(VanillaModel())
        rf.set_value('quantity', 100)
        rf.set_value('price', 600)
        rf.set_value('action', "Buy")
        rf.set_value('instrument', "GOOGL.O")
        rf.set_value('trade_date', date(2015, 5, 5))
        rf.set_value('fund', "Fund1")
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
         
    def test_create_and_save_basic(self):
        Deployer.deploy()
        trade_id = self.book_a_trade()
        s = Session()
        trades = s.query(Trade).all()
        self.assertEquals( 1, len(trades) )
        self.assertEquals( trade_id, trades[0].id)
        self.assertEquals( 100, trades[0].quantity )
        self.assertEquals( 600, trades[0].price )
        self.assertEquals( "Buy", trades[0].action.value )
        self.assertEquals( "GOOGL.O", trades[0].instrument.name )
        self.assertEquals( "USD", trades[0].currency.name )
        self.assertEquals( date(2015,5,5), trades[0].trade_date )
        self.assertEquals( date(2015,5,7), trades[0].settle_date )
        self.assertEquals( "Fund1", trades[0].portfolio.fund.name )
 
 
    def test_save_load_edit(self):
        Deployer.deploy()
        trade_id = self.book_a_trade()
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
         
        rf.set_value( 'quantity', -140)
        rf.set_value( 'price', 600)
        rf.set_value( 'action', "Sell")
        rf.set_value( 'instrument', "GOOGL.O")
        rf.set_value( 'trade_date', date(2015,5,5))
        rf.set_value( 'fund', "Fund2")
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
        Deployer.deploy()
        self.book_a_trade()
        self.book_a_trade()
        s = Session()
        trades = s.query(Trade).all()
        self.assertEquals( 2, len(trades) )
        ports = s.query(Portfolio).all()
        self.assertEquals( 1, len(ports) )


    def test_all_portfolio_attributes(self):
        Deployer.deploy()
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

        trade_id = rf.save()
        rf.load(trade_id)
        self.assertEquals( "Fund1", rf.get_value('fund' ))
        self.assertEquals( "Trader1", rf.get_value('trader' ))
        self.assertEquals( "Analyst1", rf.get_value('analyst' ))
        self.assertEquals( "Broker1", rf.get_value('broker' ))
        self.assertEquals( "Clearer1", rf.get_value('clearer' ))
        self.assertEquals( "sec1", rf.get_value('sector' ))
        self.assertEquals( "strat1", rf.get_value('strategy' ))

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

        