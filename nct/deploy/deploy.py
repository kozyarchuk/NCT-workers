from __future__ import print_function    # (at top of module)
from nct.domain import Base
from nct.utils.alch import session_scope, Session
from nct.domain.choicelist import ChoiceList
from nct.domain.entity import Entity
from nct.domain.instrument import Instrument
from datetime import date


def log_decorator(func):
    def func_wrapper(self):
        print ("%s starting..."%func.__name__, end="")
        ret = func(self)
        print ("Done")
        return ret
    return func_wrapper

class Deployer:
    
    @classmethod
    def deploy(cls):
        cls.update_schema()
        cls.update_data()
    
    @classmethod
    @log_decorator
    def update_schema(cls):
        engine  = Session().get_bind()
        Base.metadata.drop_all( engine )
        Base.metadata.create_all( engine )
        
    @classmethod
    @log_decorator
    def create_choice_lists(cls):
        with session_scope() as s:
            s.add(ChoiceList(list_name="Action", value="Buy"))
            s.add(ChoiceList(list_name="Action", value="Sell"))
            s.add(ChoiceList(list_name="InsType", value="Currency"))
            s.add(ChoiceList(list_name="InsType", value="Equity"))
            s.add(ChoiceList(list_name="InsType", value="Option"))
            s.add(ChoiceList(list_name="EntityType", value="Trader"))
            s.add(ChoiceList(list_name="EntityType", value="Analyst"))
            s.add(ChoiceList(list_name="EntityType", value="Broker"))
            s.add(ChoiceList(list_name="EntityType", value="Clearer"))
            s.add(ChoiceList(list_name="EntityType", value="Fund"))

    @classmethod
    @log_decorator
    def create_entities(cls):
        with session_scope() as s:
            s.add(Entity(name = 'Clearer1', description = 'Demo Clearer', 
                         type =ChoiceList.find(s, "EntityType", "Clearer")))
            s.add(Entity(name = 'Broker1', description = 'Demo Broker', 
                         type =ChoiceList.find(s, "EntityType", "Broker")))
            s.add(Entity(name = 'Trader1', description = 'Demo Trader', 
                         type =ChoiceList.find(s, "EntityType", "Trader")))
            s.add(Entity(name = 'Analyst1', description = 'Demo Analyst', 
                         type =ChoiceList.find(s, "EntityType", "Analyst")))
            s.add(Entity(name = 'Fund1', description = 'Demo Analyst', 
                         type =ChoiceList.find(s, "EntityType", "Fund")))
            s.add(Entity(name = 'Fund2', description = 'Demo Analyst', 
                         type =ChoiceList.find(s, "EntityType", "Fund")))

    @classmethod
    @log_decorator
    def create_instruments(cls):
        with session_scope() as s:
            usd     = Instrument(name = 'USD', ins_type = ChoiceList.find(s, "InsType", "Currency") )
            usd.currency = usd
            s.add(usd)
            eqtype = ChoiceList.find(s, "InsType", "Equity")
            googl   = Instrument(name = 'GOOGL.O', ins_type = eqtype, currency = usd )
            s.add(googl)
            s.add(Instrument(name = 'TWTR.N', ins_type = eqtype, currency = usd ))
            s.add(Instrument(name = 'GS.N', ins_type = eqtype, currency = usd ))
            s.add(Instrument(name = 'BAC.N', ins_type = eqtype, currency = usd ))
            s.add(Instrument(name = 'IBM.N', ins_type = eqtype, currency = usd ))

            opt_type = ChoiceList.find(s, "InsType", "Option")
            s.add(Instrument(name = 'GOOG150508C00540000', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))
            s.add(Instrument(name = 'GOOG150508C00542500', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))
            s.add(Instrument(name = 'GOOG150508P00527500', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))
            s.add(Instrument(name = 'GOOG150508P00530000', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))

    @classmethod
    def update_data(cls):
        cls.create_choice_lists()
        cls.create_entities()
        cls.create_instruments()
    
        