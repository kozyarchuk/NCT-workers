
from nct.domain.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship

class Trade(Base):
    __tablename__ = 'trade'
     
    id            = Column(Integer, primary_key=True)
    instrument_id = Column( Integer, ForeignKey('instrument.id'), nullable = False)
    action_id     = Column( Integer, ForeignKey('choice_list.id'), nullable = False) 
    quantity      = Column( Numeric(27,8), nullable = False)
    price         = Column( Numeric(31,12), nullable = False)
    currency_id   = Column( Integer, ForeignKey('instrument.id'), nullable = False)
    trade_date    = Column( Date , nullable = False)
    settle_date   = Column( Date , nullable = False)
    portfolio_id  = Column( Integer, ForeignKey('portfolio.id'), nullable = False)

    instrument  = relationship("Instrument",foreign_keys="[Trade.instrument_id]")
    action      = relationship("ChoiceList",foreign_keys="[Trade.action_id]")
    currency    = relationship("Instrument",foreign_keys="[Trade.currency_id]")
    portfolio   = relationship("Portfolio",foreign_keys="[Trade.portfolio_id]")



