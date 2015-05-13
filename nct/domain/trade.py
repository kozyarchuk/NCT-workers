
from nct.domain.base import Base, NotFound
from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

class Trade(Base):
    __tablename__ = 'trade'
     
    id            = Column(Integer, primary_key=True)
    trade_id      = Column( String(255), unique = True, nullable = False)
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


    @classmethod
    def find(cls, s, trade_id):
        try:
            return s.query(Trade).filter_by(trade_id = trade_id ).one()
        except NoResultFound:
            raise NotFound(">{}< Not Found".format(trade_id))

