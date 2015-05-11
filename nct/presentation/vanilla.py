from nct.utils.reactive.reactive_model import ReactiveModel
from nct.domain.trade import Trade
from nct.domain.portfolio import Portfolio
import datetime
from nct.domain.entity import Entity
from nct.domain.choicelist import ChoiceList
from nct.domain.instrument import Instrument

class VanillaModel(ReactiveModel):
    
    FIELD_DEPENDS = { 'action':[],
                      'quantity':[],
                      'price': [],
                      'instrument':[],
                      'currency':['instrument'],
                      'trade_date':[],
                      'settle_date':['trade_date'],
                      #Portfolio Fields
                      'fund':[],
                      'trader':[],
                      'analyst':[],
                      'broker':[], 
                      'clearer':[], 
                      'sector':[], 
                      'strategy':[], 
                      }

    @property
    def _trade(self):
        return self.get_domain_object(self.TRADE)

    @property
    def _port(self):
        return self.get_domain_object(self.PORTFOLIO)
        
    def calc_settle_date(self):
        return self.trade_date.value + datetime.timedelta(days=2)

    def calc_currency(self):
        return Instrument.find(self.s, self.instrument.value).currency.name

    def map_trade_action(self, field, direction):
        if direction == field.TO:
            self._trade.action = ChoiceList.find(self.s, 'Action', field.value)
        else:
            return self._trade.action.value

    def map_currency(self, field, direction):
        if direction == field.TO:
            self._trade.currency = Instrument.find(self.s, field.value)
        else:
            return self._trade.currency.name
            
    def map_instrument(self, field, direction):
        if direction == field.TO:
            self._trade.instrument = Instrument.find(self.s, field.value)
        else:
            return self._trade.instrument.name

    def map_fund(self, field, direction):
        if direction == field.TO:
            self._port.fund = Entity.find(self.s, 'Fund', field.value)
        else:
            return self._trade.portfolio.fund.name

    def save(self):
        self._trade.portfolio = self._port
        self.s.add(self._trade)
        return self._commit()
            
    def load(self, trade_id):
        self._domain_objects = {}
        self._domain_objects[self.TRADE] = self.s.query(Trade).get( trade_id )
        self._domain_objects[self.PORTFOLIO] = self._trade.portfolio
    
    def delete(self):
        self.s.delete(self._trade)
        return self._commit()

    def _init_domain_objects(self):
        return {self.TRADE: Trade(),
                self.PORTFOLIO: Portfolio()}
