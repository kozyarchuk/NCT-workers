from __future__ import print_function    # (at top of module)
from nct.domain import Base
from nct.utils.alch import engine, session_scope
from nct.domain.choicelist import ChoiceList
from nct.domain.entity import Entity
from nct.domain.instrument import Instrument
from datetime import date
from nct.domain.portfolio import Portfolio


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
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        
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

    @classmethod
    @log_decorator
    def create_entities(cls):
        with session_scope() as s:
            s.add(Entity(name = 'Clearer1', description = 'Demo Clearer', 
                         type =ChoiceList.find_by_name(s, "EntityType", "Clearer")))
            s.add(Entity(name = 'Broker1', description = 'Demo Broker', 
                         type =ChoiceList.find_by_name(s, "EntityType", "Broker")))
            s.add(Entity(name = 'Trader1', description = 'Demo Trader', 
                         type =ChoiceList.find_by_name(s, "EntityType", "Trader")))
            s.add(Entity(name = 'Analyst1', description = 'Demo Analyst', 
                         type =ChoiceList.find_by_name(s, "EntityType", "Analyst")))

    @classmethod
    @log_decorator
    def create_instruments(cls):
        with session_scope() as s:
            usd     = Instrument(name = 'USD', ins_type = ChoiceList.find_by_name(s, "InsType", "Currency") )
            usd.currency = usd
            s.add(usd)
            eqtype = ChoiceList.find_by_name(s, "InsType", "Equity")
            googl   = Instrument(name = 'GOOGL.O', ins_type = eqtype, currency = usd )
            s.add(googl)
            s.add(Instrument(name = 'TWTR.N', ins_type = eqtype, currency = usd ))
            s.add(Instrument(name = 'GS.N', ins_type = eqtype, currency = usd ))
            s.add(Instrument(name = 'BAC.N', ins_type = eqtype, currency = usd ))
            s.add(Instrument(name = 'IBM.N', ins_type = eqtype, currency = usd ))

            opt_type = ChoiceList.find_by_name(s, "InsType", "Option")
            s.add(Instrument(name = 'GOOG150508C00540000', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))
            s.add(Instrument(name = 'GOOG150508C00542500', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))
            s.add(Instrument(name = 'GOOG150508P00527500', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))
            s.add(Instrument(name = 'GOOG150508P00530000', ins_type = opt_type, 
                             currency = usd, underlying = googl, exp_date = date(2015,5,8)))


    @classmethod
    @log_decorator
    def create_portfolios(cls):
        def permutize(x):
            if x:
                first = x[0]
                rest = x[1:]
                res = []
                for i in first:
                    res.extend( [[i] + j for j in permutize(rest) ] )
                return res
            else:
                return [[]]

        with session_scope() as s:
            broker1 = s.query(Entity).filter_by(name ='Broker1').one()
            clearer1 = s.query(Entity).filter_by(name ='Clearer1').one()
            trader1 = s.query(Entity).filter_by(name ='Trader1').one()
            analyst1 = s.query(Entity).filter_by(name ='Analyst1').one()
            brokers = [None, broker1]
            clearers = [None, clearer1]
            traders = [None, trader1]
            analysts = [None, analyst1]
            categories = ['', 'cat1']
            perms = permutize([brokers, clearers, traders, analysts,categories,categories,categories])
            counter = 1
            for broker, clearer, trader, analyst,cat1,cat2,cat3 in perms:
                s.add(Portfolio(description = 'Port %i'%counter, trader = trader,
                                analyst = analyst, broker = broker, clearer =  clearer ,
                                category_1 = cat1, category_2 = cat2, category_3 = cat3))
                counter +=1


    @classmethod
    def update_data(cls):
        cls.create_choice_lists()
        cls.create_entities()
        cls.create_instruments()
#         cls.create_portfolios()
    
        