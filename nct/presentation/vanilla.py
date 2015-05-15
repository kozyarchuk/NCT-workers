from nct.utils.reactive.reactive_model import ReactiveModel
from nct.domain.trade import Trade
from nct.domain.portfolio import Portfolio
import datetime
from nct.domain.entity import Entity
from nct.domain.choicelist import ChoiceList
from nct.domain.instrument import Instrument
from nct.domain.base import NotFound

class VanillaModel(ReactiveModel):
    
    FIELD_DEPENDS = {'trade_id':[], 
                     'action':[],
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

    def _map_object_value(self, obj, field, direction, finder, obj_attr = 'name'):
        field_name = field.name
        if direction == field.TO:
            if field.value:
                setattr(obj, field_name, finder(field.value) )
            else:
                setattr(obj, field_name, None )
        else:
            entity = getattr(obj, field_name)
            if entity:
                return getattr(entity, obj_attr)

    def map_trade_action(self, field, direction):
        def finder(field_value):
            return ChoiceList.find(self.s, 'Action', field_value)
        return self._map_object_value(self._trade, field, direction, finder, 'value')

    def map_instrument(self, field, direction):
        def finder(field_value):
            return Instrument.find(self.s, field_value)
        return self._map_object_value(self._trade, field, direction, finder)
            
    def _map_port_value(self, field, direction, entity_type):
        def finder(field_value):
            return Entity.find(self.s, entity_type, field_value)
        return self._map_object_value(self._port, field, direction, finder)

    def map_fund(self, field, direction):
        return self._map_port_value(field, direction, 'Fund')

    def map_trader(self, field, direction):
        return self._map_port_value(field, direction, 'Trader')

    def map_analyst(self, field, direction):
        return self._map_port_value(field, direction, 'Analyst')

    def map_broker(self, field, direction):
        return self._map_port_value(field, direction, 'Broker')

    def map_clearer(self, field, direction):
        return self._map_port_value(field, direction, 'Clearer')

    def save(self):
        found = Portfolio.find_by_hash(self.s, self._port.get_hash_value())
        self._trade.portfolio = found if found else self._port
        trade_id = self._trade.trade_id
        self.s.add(self._trade)
        self._commit()
        return trade_id
    
    def load(self, trade_id):
        self._domain_objects = {}
        try:
            self._domain_objects[self.TRADE] = Trade.find(self.s, trade_id )
            self._domain_objects[self.PORTFOLIO] = self._trade.portfolio
        except NotFound:
            self._domain_objects = self._init_domain_objects()
        return self._trade.trade_id

    def delete(self):
        self.s.delete(self._trade)
        self._commit()

    def _init_domain_objects(self):
        return {self.TRADE: Trade(),
                self.PORTFOLIO: Portfolio()}
