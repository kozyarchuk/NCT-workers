
from nct.domain.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric

class Trade(Base):
    __tablename__ = 'trade'
     
    id            = Column(Integer, primary_key=True)
    instrument_id = Column( Integer, ForeignKey('instrument.id'))
    action        = Column( Integer, ForeignKey('choice_list.id')) 
    quantity      = Column( Numeric(27,8))
    price         = Column( Numeric(31,12))
    currency_id   = Column( Integer, ForeignKey('instrument.id'))
    trade_date    = Column( Date )
    settle_date   = Column( Date )
    portfolio_id  = Column( Integer, ForeignKey('portfolio.id'))

