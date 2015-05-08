from nct.domain.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id          = Column( Integer, primary_key=True)
    description = Column( String(255))
    trader_id   = Column( Integer, ForeignKey('entity.id'))
    analyst_id  = Column( Integer, ForeignKey('entity.id'))
    broker_id   = Column( Integer, ForeignKey('entity.id'))
    clearer_id  = Column( Integer, ForeignKey('entity.id'))
    fund_id     = Column( Integer, ForeignKey('entity.id'))
    strategy    = Column( String(255))
    sector      = Column( String(255))

    trader  = relationship("Entity",foreign_keys="[Portfolio.trader_id]")
    broker  = relationship("Entity",foreign_keys="[Portfolio.broker_id]")
    analyst = relationship("Entity",foreign_keys="[Portfolio.analyst_id]")
    clearer = relationship("Entity",foreign_keys="[Portfolio.clearer_id]")
    fund    = relationship("Entity",foreign_keys="[Portfolio.fund_id]")



