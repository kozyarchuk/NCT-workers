import unittest
from nct.domain.entity import Entity
from nct.domain.portfolio import Portfolio

class HashFunctionTest(unittest.TestCase):

    def test_hash_function_with_children(self):
        e = Entity( id = 222, name  ='xyz')
        e.description = 'bdf'
        p = Portfolio(strategy = '123', id=123)
        p.fund = e
        self.assertEquals("<Portfolio(analyst_id=None, broker_id=None, clearer_id=None, description=None, fund_id=222, id=123, sector=None, strategy='123', trader_id=None)>", p.hash_function())

    def test_hash_function_with_skips_hash_value(self):
        p1 = Portfolio(strategy = '123')
        p1.hash_value = p1.get_hash_value()
 
        self.assertEquals(p1.hash_value, p1.get_hash_value())
