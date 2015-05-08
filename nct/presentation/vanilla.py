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

    def calc_settle_date(self):
        return self.trade_date.value + datetime.timedelta(days=2)

    def calc_currency(self):
        return Instrument.find(self.s, self.instrument.value).currency.name

    def map_trade_action(self, field, direction):
        if direction == field.TO:
            self.get_domain_object(self.TRADE).action = ChoiceList.find_by_name(self.s, 'Action', field.value)

    def map_currency(self, field, direction):
        if direction == field.TO:
            self.get_domain_object(self.TRADE).currency = Instrument.find(self.s, field.value)
            
    def map_instrument(self, field, direction):
        if direction == field.TO:
            self.get_domain_object(self.TRADE).instrument = Instrument.find(self.s, field.value)

    def map_fund(self, field, direction):
        if direction == field.TO:
            self.get_domain_object(self.PORTFOLIO).fund = Entity.find(self.s, 'Fund', field.value)

    def save(self):
        trade = self.get_domain_object(self.TRADE)
        portfolio = self.get_domain_object(self.PORTFOLIO)
        trade.portfolio = portfolio
        try:
            self.s.add(portfolio)
            self.s.add(trade)
            self.s.commit()
        except:
            self.s.rollback()
            raise
            
    def _init_domain_objects(self):
        return {self.TRADE: Trade(),
                self.PORTFOLIO: Portfolio()}
