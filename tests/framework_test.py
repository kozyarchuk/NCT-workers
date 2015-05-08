import unittest
from nct.domain.instrument import Instrument
from nct.domain.trade import Trade
from nct.utils.reactive.framework import ReactiveFramework
from datetime import date
from decimal import Decimal
from nct.utils.reactive.reactive_model import ReactiveModel


class StubModel(ReactiveModel):
    FIELD_DEPENDS = { 'quantity':[],
                     'trade_date':[],
                     'currency':[],
                     'calendar':['currency'],
                     'settle_date':['trade_date', 'calendar'],
                     'commission':['trade_date', 'quantity'] }

    def _init_domain_objects(self):
        return {self.INSTRUMENT:  Instrument(),
                self.TRADE:  Trade() }
    
    def calc_commission(self):
        return Decimal(100)

    def calc_calendar(self):
        return  "US"

    def calc_settle_date(self):
        return date(2015,2,2)
    
    def calc_currency(self):
        pass
    
    def map_currency(self, field, direction):
        if direction == field.TO:
            self.get_domain_object(self.TRADE).currency = field.value
        else:
            return self.get_domain_object(self.TRADE).currency
    
    def save(self):
        self.save_called =True
    
    def load(self, trade_id):
        self.load_called = trade_id

class FrameWorkTest(unittest.TestCase):
    
    def test_can_create_rf(self):
        m = StubModel()
        m.FIELD_DEPENDS = { 'quantity':[] }
        rf = ReactiveFramework(m)
        self.assertEqual(m, rf.model)
        self.assertEquals({}, rf.depends_notifty)
        self.assertEquals(None, rf.model.quantity.value)
    
    def test_depends_notify(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        self.assertEqual(sorted(['calendar', 'currency','quantity', 'trade_date']), sorted(rf.depends_notifty.keys()))
        self.assertEqual(['calendar'], rf.depends_notifty['currency'])
        self.assertEqual(['settle_date'], rf.depends_notifty['calendar'])
        self.assertEqual(sorted(['settle_date','commission']), sorted(rf.depends_notifty['trade_date']))
        
    def test_are_dependent_set_no_depends(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        self.assertTrue( rf._are_dependents_set( 'quantity' ) )

    def test_are_dependent_set_one_depends(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        self.assertFalse(rf._are_dependents_set( 'calendar' ) )
        rf.set_value('currency', 'USD')
        self.assertTrue(rf._are_dependents_set( 'calendar' ) )

    def test_are_dependent_set_two_depends(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        self.assertFalse(rf._are_dependents_set( 'settle_date' ) )
        rf.set_value('trade_date', date(2015,1,1))
        self.assertFalse(rf._are_dependents_set( 'settle_date' ) )
        rf.set_value('calendar', 'USD')
        self.assertTrue(rf._are_dependents_set( 'settle_date' ) )

    def test_set_field_recalcs(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        self.assertEquals([], rf.set_value('quantity', 100))
        self.assertEquals(['commission'], rf.set_value('trade_date', date(2015,2,1)))
        self.assertEquals(['commission'], rf.set_value('quantity', 150))
        self.assertListEqual(sorted(['calendar', 'settle_date']), sorted(rf.set_value('currency', 'USD')))
        self.assertListEqual(sorted(['commission', 'settle_date']), sorted(rf.set_value('trade_date', date(2015,2,1))))
        self.assertEquals([], rf.set_value('commission', 4))
        self.assertEquals(['settle_date'], rf.set_value('trade_date', date(2015,2,1)))
        self.assertEquals('USD', rf.get_value('currency'))
        self.assertEquals( date(2015,2,1), rf.get_value('trade_date'))
        self.assertEquals( date(2015,2,2), rf.get_value('settle_date'))
        self.assertEquals( 4, rf.get_value('commission'))
        self.assertEquals( "US", rf.get_value('calendar'))
        
    def test_validate(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        self.assertDictEqual({'commission': 'Not set',  'currency': 'Not set',
                              'quantity': 'Not set', 'settle_date': 'Not set', 
                              'trade_date': 'Not set'}, rf.validate())
        
    def test_save(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        rf.set_value('quantity', 100)
        rf.save()

        trade = m.get_domain_object('Trade')
        self.assertEquals(trade.quantity, rf.get_value('quantity'))
        self.assertTrue(m.save_called)

    def test_load(self):
        m = StubModel()
        rf = ReactiveFramework(m)
        trade = m.get_domain_object('Trade')
        trade.quantity = Decimal("100")
        trade.trade_date = date(2015,2,1)
        trade.settle_date = date(2015,2,3)
        trade.currency = 'EUR'
        rf.load(123)
        self.assertEqual(123, m.load_called)
        self.assertEqual(100, rf.get_value('quantity'))
        self.assertEqual(date(2015,2,1), rf.get_value('trade_date'))
        self.assertEqual(date(2015,2,3), rf.get_value('settle_date'))
        self.assertEqual('EUR', rf.get_value('currency'))
        self.assertEqual('US', rf.get_value('calendar'))
        self.assertEqual(100, rf.get_value('commission'))
        
        for field in rf.get_fields():
            self.assertEquals(False, field.has_user_entered_value)
        
